import multiprocessing
from multiprocessing.managers import ListProxy, ValueProxy, DictProxy
import warnings

import os
import signal
from collections import deque
from typing import Any
from common.map_enums import QueueType, ProcessingStatus, MapConfigKeys, SharedDictKeys, TaskQueueKeys
from modules.main_generator import generate_map
from modules.utils import Utils
from modules.gpx_manager import GpxManager
import psutil


class MapTaskQueueManager:
    def __init__(self, max_normal_tasks, max_preview_tasks, gpx_tmp_folder, gpx_crs):
        self.max_normal_tasks = max_normal_tasks
        self.max_preview_tasks = max_preview_tasks
        self.gpx_tmp_folder = gpx_tmp_folder
        self.gpx_crs = gpx_crs
        self.manager = multiprocessing.Manager()

        self.running_normal_processes: ValueProxy[int] = self.manager.Value(
            'i', 0)
        self.running_preview_processes: ValueProxy[int] = self.manager.Value(
            'i', 0)

        self.normal_queue: ListProxy[Any] = self.manager.list()
        self.preview_queue = self.manager.list()
        self.queue_lock = multiprocessing.Lock()

    def add_task(self, map_generator_config, task_id, shared_tasks, shared_tasks_lock, queue_type=QueueType.NORMAL):
        """Add a task to the appropriate queue or start it if possible"""
        task_item = {
            TaskQueueKeys.CONFIG.value: map_generator_config,
            TaskQueueKeys.TASK_ID.value: task_id,
            TaskQueueKeys.QUEUE_TYPE.value: queue_type
        }
        with shared_tasks_lock:
            shared_tasks[task_id] = {
                SharedDictKeys.STATUS.value: ProcessingStatus.IN_QUEUE.value,
                SharedDictKeys.FILES.value: [],
                SharedDictKeys.PROCESS_RUNNING.value: False,
                SharedDictKeys.PID.value: None,
                SharedDictKeys.IS_PREVIEW.value: queue_type == QueueType.PREVIEW
            }

        with self.queue_lock:
            can_start = False
            if queue_type == QueueType.NORMAL and self.running_normal_processes.value < self.max_normal_tasks:
                can_start = True
                self.running_normal_processes.value += 1
            elif queue_type == QueueType.PREVIEW and self.running_preview_processes.value < self.max_preview_tasks:
                can_start = True
                self.running_preview_processes.value += 1

            if can_start:
                with shared_tasks_lock:
                    shared_tasks[task_id] = {
                        SharedDictKeys.STATUS.value: ProcessingStatus.STARTING.value,
                        SharedDictKeys.FILES.value: [],
                        SharedDictKeys.PROCESS_RUNNING.value: False,
                        SharedDictKeys.PID.value: None,
                        SharedDictKeys.IS_PREVIEW.value: queue_type == QueueType.PREVIEW
                    }

                # Start the process directly
                self.__start_task_process(
                    task_item, shared_tasks, shared_tasks_lock)

                return ProcessingStatus.STARTING.value
            else:

                # Add to queue
                if queue_type == QueueType.NORMAL:
                    self.normal_queue.append(task_item)
                else:
                    self.preview_queue.append(task_item)

                return ProcessingStatus.IN_QUEUE.value

    def __start_task_process(self, task_item, shared_tasks, shared_tasks_lock):
        """Start a process that is not in the queue"""
        config = task_item[TaskQueueKeys.CONFIG.value]
        task_id = task_item[TaskQueueKeys.TASK_ID.value]
        queue_type = task_item[TaskQueueKeys.QUEUE_TYPE.value]
        if (queue_type == QueueType.NORMAL):
            process_count = self.running_normal_processes
            max_process_count = self.max_normal_tasks
            queue = self.normal_queue
        else:
            process_count = self.running_preview_processes
            max_process_count = self.max_preview_tasks
            queue = self.preview_queue
        process = multiprocessing.Process(
            target=MapTaskQueueManager._wrapped_generate_map,
            args=(config, task_id, shared_tasks, shared_tasks_lock,
                  self.queue_lock, queue, process_count, max_process_count)
        )

        process.start()

        with shared_tasks_lock:
            shared_tasks[task_id] = {
                **shared_tasks[task_id],
                SharedDictKeys.STATUS.value: ProcessingStatus.STARTING.value,
                SharedDictKeys.PID.value: process.pid,
                SharedDictKeys.PROCESS_RUNNING.value: True
            }

    def terminate_task(self, task_id, shared_tasks: DictProxy[str, Any], shared_tasks_lock, delete_from_shared=True):
        """Terminate a task whether it's in queue or processing and clean up files"""
        with self.queue_lock:
            # Check if the task is in the queues
            removed_from_queue = False
            queue_type = None
            # Check normal queue
            for i, task in enumerate(self.normal_queue):
                if task[TaskQueueKeys.TASK_ID.value] == task_id:
                    self.normal_queue.remove(task)
                    removed_from_queue = True
                    queue_type = QueueType.NORMAL
                    break

            # Check preview queue
            if not removed_from_queue:
                for i, task in enumerate(self.preview_queue):
                    if task[TaskQueueKeys.TASK_ID.value] == task_id:
                        self.preview_queue.remove(task)
                        removed_from_queue = True
                        queue_type = QueueType.PREVIEW
                        break

            # If found in queue, just update status and clean files
            if removed_from_queue:
                with shared_tasks_lock:
                    if task_id in shared_tasks:
                        MapTaskQueueManager._clean_task_files(
                            shared_tasks[task_id][SharedDictKeys.FILES.value])
                        if (delete_from_shared):
                            shared_tasks.pop(task_id)
                        else:
                            shared_tasks[task_id] = {
                                **shared_tasks[task_id],
                                SharedDictKeys.STATUS.value: ProcessingStatus.CANCELLED.value,
                                SharedDictKeys.FILES.value: []
                            }
                return True

            with shared_tasks_lock:
                if task_id in shared_tasks and shared_tasks[task_id][SharedDictKeys.PROCESS_RUNNING.value]:
                    pid = shared_tasks[task_id][SharedDictKeys.PID.value]
                    is_preview = shared_tasks[task_id][SharedDictKeys.IS_PREVIEW.value]
                    queue_type = QueueType.PREVIEW if is_preview else QueueType.NORMAL
                    # need to handle carefully -> can drop whole server
                    if (pid is not None):
                        process = psutil.Process(pid)
                        if (process is not None and process.is_running()):
                            for child in process.children(recursive=True):
                                try:
                                    if(child.is_running()):
                                        child.terminate()
                                except:
                                    warnings.warn(
                                        f"Failed to terminate child process {child.pid} for task {task_id} using SIGTERM")
                                    try:
                                        if(child.is_running()):
                                            child.kill()
                                    except:
                                        warnings.warn(
                                            f"Failed to terminate child process for task {task_id} using SIGKILL")
                            try:
                                if(process.is_running()):
                                    process.terminate()
                            except:
                                warnings.warn(
                                    f"Failed to terminate process {pid} for task {task_id} using SIGTERM")
                                try:
                                    if(process.is_running()):
                                        process.kill()
                                except:
                                    warnings.warn(
                                        f"Failed to terminate process for task {task_id} using SIGKILL")

                    MapTaskQueueManager._clean_task_files(
                        shared_tasks[task_id][SharedDictKeys.FILES.value])
                    if (delete_from_shared):
                        shared_tasks.pop(task_id)
                    else:
                        shared_tasks[task_id] = {
                            **shared_tasks[task_id],
                            SharedDictKeys.STATUS.value: ProcessingStatus.CANCELLED.value,
                            SharedDictKeys.PROCESS_RUNNING.value: False,
                            SharedDictKeys.PID.value: None,
                            SharedDictKeys.FILES.value: []
                        }

                     # start next task if any
                    if queue_type == QueueType.NORMAL:
                        self.running_normal_processes.value -= 1
                        # Start new normal task
                        if self.normal_queue and self.running_normal_processes.value < self.max_normal_tasks:
                            next_task = self.normal_queue.pop(0)
                            self.running_normal_processes.value += 1
                            self.__start_task_process(
                                next_task, shared_tasks, shared_tasks_lock)
                    else:
                        self.running_preview_processes.value -= 1
                        # Start new preview task
                        if self.preview_queue and self.running_preview_processes.value < self.max_preview_tasks:
                            next_task = self.preview_queue.pop(0)
                            self.running_preview_processes.value += 1
                            self.__start_task_process(
                                next_task, shared_tasks, shared_tasks_lock)
                    return True

                if task_id in shared_tasks:
                    MapTaskQueueManager._clean_task_files(
                        shared_tasks[task_id][SharedDictKeys.FILES.value])
                    if (delete_from_shared):
                        shared_tasks.pop(task_id)
                    else:
                        shared_tasks[task_id] = {
                            **shared_tasks[task_id],
                            SharedDictKeys.STATUS.value: ProcessingStatus.CANCELLED.value,
                            SharedDictKeys.FILES.value: [],
                        }
                    return True
            return False

    def clean_queue(self, shared_tasks, shared_tasks_lock):
        """Clear tasks with files from queues. Cleared tasks will have status CANCELLED"""
        with self.queue_lock:
            # Update status for all tasks in both queues
            with shared_tasks_lock:
                for task in self.normal_queue:
                    task_id = task[TaskQueueKeys.TASK_ID.value]
                    if task_id in shared_tasks:
                        MapTaskQueueManager._clean_task_files(
                            shared_tasks[task_id][SharedDictKeys.FILES.value])
                        shared_tasks[task_id] = {
                            **shared_tasks[task_id],
                            SharedDictKeys.STATUS.value: ProcessingStatus.CANCELLED.value,
                            SharedDictKeys.FILES.value: []
                        }

                for task in self.preview_queue:
                    task_id = task[TaskQueueKeys.TASK_ID.value]
                    if task_id in shared_tasks:
                        MapTaskQueueManager._clean_task_files(
                            shared_tasks[task_id][SharedDictKeys.FILES.value])
                        shared_tasks[task_id] = {
                            **shared_tasks[task_id],
                            SharedDictKeys.STATUS.value: ProcessingStatus.CANCELLED.value,
                            SharedDictKeys.FILES.value: []
                        }
            self.normal_queue = []
            self.preview_queue = []

    @staticmethod
    def _wrapped_generate_map(config, task_id, shared_tasks, shared_tasks_lock, queue_lock, queue: ListProxy[Any], running_process_count: ValueProxy[int], max_process_count):
        try:
            generate_map(config, task_id, shared_tasks, shared_tasks_lock)

            with shared_tasks_lock:
                shared_tasks[task_id] = {
                    **shared_tasks[task_id],
                    SharedDictKeys.STATUS.value: ProcessingStatus.FINISHED.value,
                    SharedDictKeys.PROCESS_RUNNING.value: False,
                    SharedDictKeys.PID.value: None
                }
        except Exception as e:
            warnings.warn(
                f"Failed to process task (generate map) {task_id}: {str(e)}")
            with shared_tasks_lock:
                MapTaskQueueManager._clean_task_files(
                    shared_tasks[task_id][SharedDictKeys.FILES.value])
                shared_tasks[task_id] = {
                    **shared_tasks[task_id],
                    SharedDictKeys.FILES.value: [],
                    SharedDictKeys.STATUS.value: ProcessingStatus.FAILED.value,
                    SharedDictKeys.PROCESS_RUNNING.value: False,
                    SharedDictKeys.PID.value: None,
                }

        finally:
            with queue_lock:
                # start next task if any
                running_process_count.value -= 1
                if queue and running_process_count.value < max_process_count:
                    next_task = queue.pop(0)
                    next_config = next_task[TaskQueueKeys.CONFIG.value]
                    next_task_id = next_task[TaskQueueKeys.TASK_ID.value]
                    running_process_count.value += 1
                    process = multiprocessing.Process(
                        target=MapTaskQueueManager._wrapped_generate_map,
                        args=(next_config, next_task_id, shared_tasks, shared_tasks_lock,
                              queue_lock, queue, running_process_count, max_process_count)
                    )
                    process.start()
                    with shared_tasks_lock:
                        shared_tasks[next_task_id] = {
                            **shared_tasks[next_task_id],
                            SharedDictKeys.STATUS.value: ProcessingStatus.STARTING.value,
                            SharedDictKeys.PID.value: process.pid,
                            SharedDictKeys.PROCESS_RUNNING.value: True
                        }

    @staticmethod
    def _clean_task_files(files_list):
        for file_path in files_list:
            Utils.remove_file(file_path)
