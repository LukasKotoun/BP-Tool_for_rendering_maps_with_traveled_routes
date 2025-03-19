import multiprocessing
from multiprocessing.managers import ListProxy, ValueProxy, DictProxy
import warnings
from uuid_extensions import uuid7str

import os
import signal
from collections import deque
from typing import Any
from common.map_enums import QueueType, ProcessingStatus, MapConfigKeys, SharedDictKeys, TaskQueueKeys
from modules.main_generator import generate_map
from modules.utils import Utils
from modules.gpx_manager import GpxManager
import psutil

class TaskManager:
    def __init__(self, max_normal_tasks, max_preview_tasks, gpx_tmp_folder, gpx_crs):
        self.max_normal_tasks = max_normal_tasks
        self.max_preview_tasks = max_preview_tasks
        self.gpx_tmp_folder = gpx_tmp_folder
        self.gpx_crs = gpx_crs

        self.manager = multiprocessing.Manager()
        self.shared_tasks: DictProxy[str, Any] = self.manager.dict()

        # always use with queue_lock
        self.running_normal_processes: ValueProxy[int] = self.manager.Value(
            'i', 0)
        self.running_preview_processes: ValueProxy[int] = self.manager.Value(
            'i', 0)

        self.normal_queue: ListProxy[Any] = self.manager.list()
        self.preview_queue = self.manager.list()
        # need to use multiprocessing.Lock() instead of manager.Lock() 
        # manager.lock will not free lock after process that aquire it is terminated 
        # self.shared_tasks_lock = self.manager.Lock()
        self.shared_tasks_lock = multiprocessing.Lock()
        self.queue_lock = multiprocessing.Lock()

    def add_task(self, map_generator_config, queue_type=QueueType.NORMAL):
        """Add a task to the appropriate queue or start it if possible"""
        task_id = uuid7str()
        task_item = {
            TaskQueueKeys.CONFIG.value: map_generator_config,
            TaskQueueKeys.TASK_ID.value: task_id,
            TaskQueueKeys.QUEUE_TYPE.value: queue_type
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
                # Start the process directly
                pid = self.__start_task_process(
                    task_item)
                if(pid is None):
                    return ProcessingStatus.FAILED.value, None
                with self.shared_tasks_lock:
                    self.shared_tasks[task_id] = {
                        SharedDictKeys.STATUS.value: ProcessingStatus.STARTING.value,
                        SharedDictKeys.FILES.value: [],
                        SharedDictKeys.PROCESS_RUNNING.value: True,
                        SharedDictKeys.PID.value: pid,
                        SharedDictKeys.IS_PREVIEW.value: queue_type == QueueType.PREVIEW
                    }
                return ProcessingStatus.STARTING.value, task_id
            else:
                with self.shared_tasks_lock:
                    self.shared_tasks[task_id] = {
                        SharedDictKeys.STATUS.value: ProcessingStatus.IN_QUEUE.value,
                        SharedDictKeys.FILES.value: [],
                        SharedDictKeys.PROCESS_RUNNING.value: False,
                        SharedDictKeys.PID.value: None,
                        SharedDictKeys.IS_PREVIEW.value: queue_type == QueueType.PREVIEW
                    }
                # Add to queue
                if queue_type == QueueType.NORMAL:
                    self.normal_queue.append(task_item)
                else:
                    self.preview_queue.append(task_item)

                return ProcessingStatus.IN_QUEUE.value, task_id

    def __start_task_process(self, task_item) -> int:
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
            target=TaskManager._wrapped_generate_map,
            args=(config, task_id, self.shared_tasks, self.shared_tasks_lock,
                  self.queue_lock, queue, process_count, max_process_count)
        )

        process.start()
        return process.pid
    def delete_task(self, task_id):
        """Delete a task whether it's in queue, running in paralel process or completed and clean up files if needed"""
        with self.shared_tasks_lock:
            if (task_id is None or task_id == "" or task_id not in self.shared_tasks):
                return False
            else:
                task_info = self.shared_tasks[task_id]
            # check if task is completed stats wont be updating
            if(task_info[SharedDictKeys.STATUS.value] == ProcessingStatus.COMPLETED.value):
                TaskManager._clean_task_files(
                    task_info[SharedDictKeys.FILES.value])
                self.shared_tasks.pop(task_id)
                return True
        
        # check if task is in queue
        if(task_info[SharedDictKeys.STATUS.value] == ProcessingStatus.IN_QUEUE.value):       
            queue_type = QueueType.PREVIEW if task_info[
                SharedDictKeys.IS_PREVIEW.value] else QueueType.NORMAL
            with self.queue_lock:
                removed_from_queue = False
                if (queue_type == QueueType.PREVIEW):
                    for i, task in enumerate(self.preview_queue):
                        if task[TaskQueueKeys.TASK_ID.value] == task_id:
                            self.preview_queue.remove(task)
                            removed_from_queue = True
                            break

                elif (queue_type == QueueType.NORMAL):
                    for i, task in enumerate(self.normal_queue):
                        if task[TaskQueueKeys.TASK_ID.value] == task_id:
                            self.normal_queue.remove(task)
                            removed_from_queue = True
                            break
            # found in queue -> delete and clean files
            if removed_from_queue:
                with self.shared_tasks_lock:
                    if task_id in self.shared_tasks:
                        TaskManager._clean_task_files(
                            self.shared_tasks[task_id][SharedDictKeys.FILES.value])
                        self.shared_tasks.pop(task_id)
                return True
            
        # task is in other state
        can_start_next = False
        queue_type = None
        # lock so that it dont terminate task if that task is using the shared_tasks dict
        with self.shared_tasks_lock:
            # check again - shared_tasks might have been updated - prevent errors in extarcting task self.shared_tasks[task_id]
            if(task_id not in self.shared_tasks):
                return False
            task_info = self.shared_tasks[task_id]
            # check if task is running and terminate it
            if task_info[SharedDictKeys.PROCESS_RUNNING.value]:
                # terminate running process
                pid = task_info[SharedDictKeys.PID.value]
                queue_type = QueueType.PREVIEW if task_info[SharedDictKeys.IS_PREVIEW.value] else QueueType.NORMAL
                can_start_next = True
                # need to handle carefully -> can drop whole server
                if (pid is not None):
                    process = psutil.Process(pid)
                    if (process is not None and process.is_running()):
                        for child in process.children(recursive=True):
                            try:
                                if (child.is_running()):
                                    child.terminate()
                            except:
                                warnings.warn(
                                    f"Failed to terminate child process {child.pid} for task {task_id} using SIGTERM")
                                try:
                                    if (child.is_running()):
                                        child.kill()
                                except:
                                    warnings.warn(
                                        f"Failed to terminate child process for task {task_id} using SIGKILL")
                        try:
                            if (process.is_running()):
                                process.terminate()
                        except:
                            warnings.warn(
                                f"Failed to terminate process {pid} for task {task_id} using SIGTERM")
                            try:
                                if (process.is_running()):
                                    process.kill()
                            except:
                                warnings.warn(
                                    f"Failed to terminate process for task {task_id} using SIGKILL")          
            # clean files and remove task from shared_tasks if in other state           
            TaskManager._clean_task_files(
                task_info[SharedDictKeys.FILES.value])
            self.shared_tasks.pop(task_id)

        # check if previous task was running so that we can try to start next task
        if(can_start_next and queue_type is not None):
            with self.queue_lock:
                next_task = None
                if queue_type == QueueType.NORMAL:
                    self.running_normal_processes.value -= 1
                    # Start new normal task
                    if self.normal_queue and self.running_normal_processes.value < self.max_normal_tasks:
                        next_task = self.normal_queue.pop(0)
                        self.running_normal_processes.value += 1                            
                else:
                    self.running_preview_processes.value -= 1
                    # Start new preview task
                    if self.preview_queue and self.running_preview_processes.value < self.max_preview_tasks:
                        next_task = self.preview_queue.pop(0)
                        self.running_preview_processes.value += 1
                # next task found -> start it
                if(next_task is not None):
                    pid = self.__start_task_process(
                        next_task)
                    if(pid is not None):
                        with self.shared_tasks_lock:
                            self.shared_tasks[next_task[TaskQueueKeys.TASK_ID.value]] = {
                                SharedDictKeys.STATUS.value: ProcessingStatus.STARTING.value,
                                SharedDictKeys.FILES.value: [],
                                SharedDictKeys.PROCESS_RUNNING.value: True,
                                SharedDictKeys.PID.value: pid,
                                SharedDictKeys.IS_PREVIEW.value: queue_type == QueueType.PREVIEW # must be same as previous task 
                            }
        return True
            
    def clear_queues(self):
        """Clear tasks with files from queues. Cleared tasks will be removed from shared_tasks"""
        with self.queue_lock:
            # Update status for all tasks in both queues
            for task in self.normal_queue:
                task_id = task[TaskQueueKeys.TASK_ID.value]
                with self.shared_tasks_lock:
                    if task_id in self.shared_tasks:
                        TaskManager._clean_task_files(
                            self.shared_tasks[task_id][SharedDictKeys.FILES.value])
                        self.shared_tasks.pop(task_id)

            for task in self.preview_queue:
                task_id = task[TaskQueueKeys.TASK_ID.value]
                with self.shared_tasks_lock:
                    if task_id in self.shared_tasks:
                        TaskManager._clean_task_files(
                            self.shared_tasks[task_id][SharedDictKeys.FILES.value])
                        self.shared_tasks.pop(task_id)
            self.normal_queue = []
            self.preview_queue = []

            
    def delete_all_tasks(self):
        """Delete all tasks in both queues and processing"""
        self.clear_queues()
        with self.shared_tasks_lock:
            shared_tasks_ids = self.shared_tasks.keys()
        for task_id in shared_tasks_ids:
            try:
                self.delete_task(task_id)
            except Exception as e:
                print(f"Error terminating task {task_id}: {e}")

    def get_task_info(self, task_id: str) -> dict[str, Any] | None:
        """Get info of specific task"""
        with self.shared_tasks_lock:
            if (task_id in self.shared_tasks):
                return self.shared_tasks[task_id]
            else:
                return None
            
    @staticmethod
    def _wrapped_generate_map(config, task_id, shared_tasks, shared_tasks_lock, queue_lock, queue: ListProxy[Any], running_process_count: ValueProxy[int], max_process_count):
        try:
            generate_map(config, task_id, shared_tasks, shared_tasks_lock)

            with shared_tasks_lock:
                shared_tasks[task_id] = {
                    **shared_tasks[task_id],
                    SharedDictKeys.STATUS.value: ProcessingStatus.COMPLETED.value,
                    SharedDictKeys.PROCESS_RUNNING.value: False,
                    SharedDictKeys.PID.value: None
                }
        except Exception as e:
            warnings.warn(
                f"Failed to process task (generate map) {task_id}: {str(e)}")
            with shared_tasks_lock:
                TaskManager._clean_task_files(
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
                        target=TaskManager._wrapped_generate_map,
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
