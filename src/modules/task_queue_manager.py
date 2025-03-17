import multiprocessing
from multiprocessing.managers import ListProxy, ValueProxy
import warnings

import os
import signal
from collections import deque
from typing import Any
from common.map_enums import QueueType, ProcessingStatus, MapConfigKeys
from modules.main_generator import generate_map
from modules.utils import Utils
from modules.gpx_manager import GpxManager


class MapTaskQueueManager:
    def __init__(self, max_normal_tasks, max_preview_tasks, gpx_tmp_folder, gpx_crs):
        self.max_normal_tasks = max_normal_tasks
        self.max_preview_tasks = max_preview_tasks
        self.gpx_tmp_folder = gpx_tmp_folder
        self.gpx_crs = gpx_crs
        self.manager = multiprocessing.Manager()

        self.running_normal_processes: ValueProxy[int] = self.manager.Value('i', 0)
        self.running_preview_processes: ValueProxy[int] = self.manager.Value('i', 0)

        self.normal_queue: ListProxy[Any] = self.manager.list()
        self.preview_queue = self.manager.list()
        self.queue_lock = multiprocessing.Lock()

    def add_task(self, map_generator_config, task_id, shared_tasks, shared_tasks_lock, queue_type=QueueType.NORMAL):
        """Add a task to the appropriate queue or start it if possible"""
        task_item = {
            "config": map_generator_config,
            "task_id": task_id,
            "queue_type": queue_type
        }
        with shared_tasks_lock:
            shared_tasks[task_id] = {
                "status": ProcessingStatus.IN_QUEUE.value,
                "files": [],
                "process_running": False,
                "pid": None,
                "is_preview": queue_type == QueueType.PREVIEW
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
                        "status": ProcessingStatus.STARTING.value,
                        "files": [],
                        "process_running": False,
                        "pid": None,
                        "is_preview": queue_type == QueueType.PREVIEW
                    }
                
                # Start the process directly
                self._start_task_process(
                    task_item, shared_tasks, shared_tasks_lock)

                return ProcessingStatus.STARTING.value
            else:             
               
                # Add to queue
                if queue_type == QueueType.NORMAL:
                    self.normal_queue.append(task_item)
                else:
                    self.preview_queue.append(task_item)

                return ProcessingStatus.IN_QUEUE.value
    @staticmethod
    def _wrapped_generate_map(config, task_id, shared_tasks, shared_tasks_lock, queue_lock, queue: ListProxy[Any], running_process_count: ValueProxy[int], max_process_count):
        try:
            generate_map(config, task_id, shared_tasks, shared_tasks_lock)

            with shared_tasks_lock:
                shared_tasks[task_id] = {
                    **shared_tasks[task_id],
                    "status": ProcessingStatus.FINISHED.value,
                    "process_running": False
                }

        except Exception as e:
            warnings.warn(f"Failed to process task (generate map) {task_id}: {str(e)}")
            with shared_tasks_lock:
                shared_tasks[task_id] = {
                    **shared_tasks[task_id],
                    "status": ProcessingStatus.FAILED.value,
                    "message": str(e),
                    "process_running": False
                }
                MapTaskQueueManager._clean_task_files(shared_tasks[task_id].get("files", []))

        finally:
            with queue_lock:
                    running_process_count.value -= 1
                    if queue and running_process_count.value < max_process_count:
                        next_task = queue.pop(0)
                        next_config = next_task["config"]
                        next_task_id = next_task["task_id"]
                        running_process_count.value += 1
                        process = multiprocessing.Process(
                            target=MapTaskQueueManager._wrapped_generate_map,
                            args=(next_config, next_task_id, shared_tasks, shared_tasks_lock, queue_lock, queue, running_process_count, max_process_count)
                        )
                        process.start()
                        with shared_tasks_lock:
                            shared_tasks[next_task_id] = {
                                **shared_tasks[next_task_id],
                                "status": ProcessingStatus.STARTING.value,
                                "pid": process.pid,
                                "process_running": True
                            } 

    def _start_task_process(self, task_item, shared_tasks, shared_tasks_lock):
        """Start a process """
        config = task_item["config"]
        task_id = task_item["task_id"]
        queue_type = task_item["queue_type"]
        if(queue_type == QueueType.NORMAL):
            process_count = self.running_normal_processes
            max_process_count = self.max_normal_tasks
            queue = self.normal_queue
        else:
            process_count = self.running_preview_processes
            max_process_count = self.max_preview_tasks
            queue = self.preview_queue
        process = multiprocessing.Process(
            target=self._wrapped_generate_map,
            args=(config, task_id, shared_tasks, shared_tasks_lock, self.queue_lock, queue, process_count, max_process_count)
        )

        process.start()

        with shared_tasks_lock:
            shared_tasks[task_id] = {
                **shared_tasks[task_id],
                "status": ProcessingStatus.STARTING.value,
                "pid": process.pid,
                "process_running": True
            }

    def terminate_task(self, task_id, shared_tasks, shared_tasks_lock):
        """Terminate a task whether it's in queue or processing and clean up files"""
        with self.queue_lock:
            # Check if the task is in the queues
            removed_from_queue = False
            queue_type = None
            # Check normal queue
            for i, task in enumerate(self.normal_queue):
                if task["task_id"] == task_id:
                    self.normal_queue.remove(task)
                    removed_from_queue = True
                    queue_type = QueueType.NORMAL
                    break

            # Check preview queue
            if not removed_from_queue:
                for i, task in enumerate(self.preview_queue):
                    if task["task_id"] == task_id:
                        self.preview_queue.remove(task)
                        removed_from_queue = True
                        queue_type = QueueType.PREVIEW
                        break

            # If found in queue, just update status and clean files
            if removed_from_queue:
                with shared_tasks_lock:
                    if task_id in shared_tasks:
                        MapTaskQueueManager._clean_task_files(
                            shared_tasks[task_id]["files"])
                        shared_tasks[task_id] = {
                            **shared_tasks[task_id],
                            "status": ProcessingStatus.CANCELLED.value,
                            "files": []
                        }
                return True

            with shared_tasks_lock:
                if task_id in shared_tasks and shared_tasks[task_id]['process_running']:
                    pid = shared_tasks[task_id]['pid']
                    is_preview = shared_tasks[task_id]['is_preview']
                    queue_type = QueueType.PREVIEW if is_preview else QueueType.NORMAL
                    try:
                        if pid:
                            os.kill(pid, signal.SIGTERM)
                    except:
                        warnings.warn(
                            f"Failed to terminate process {pid} for task {task_id} using SIGTERM")
                        try:
                            if (pid):
                                os.kill(pid, signal.SIGKILL)
                        except:
                            warnings.warn(
                                f"Failed to terminate process {pid} for task {task_id} using SIGKILL")

                    MapTaskQueueManager._clean_task_files(
                        shared_tasks[task_id]["files"])
                    
                    
                    if queue_type == QueueType.NORMAL:
                        self.running_normal_processes.value -= 1
                        # Start new normal task
                        if self.normal_queue and self.running_normal_processes.value < self.max_normal_tasks:
                            next_task = self.normal_queue.pop(0)
                            self.running_normal_processes.value += 1
                            self._start_task_process(
                                next_task, shared_tasks, shared_tasks_lock)
                    else:
                        self.running_preview_processes.value -= 1
                        # Start new preview task
                        if self.preview_queue and self.running_preview_processes.value < self.max_preview_tasks:
                            next_task = self.preview_queue.pop(0)
                            self.running_preview_processes.value += 1
                            self._start_task_process(
                                next_task, shared_tasks, shared_tasks_lock)
                    return True
                
                if task_id in shared_tasks:
                    MapTaskQueueManager._clean_task_files(
                        shared_tasks[task_id]['files'])
                    shared_tasks[task_id] = {
                            **shared_tasks[task_id],
                            "status": ProcessingStatus.CANCELLED.value,
                            "files": []
                            }
                    return True
            return False

            
    @staticmethod
    def _clean_task_files(files_list):
        for file_path in files_list:
            Utils.remove_file(file_path)

    def clear_queue(self, shared_tasks, shared_tasks_lock):
        """Clear tasks from both queues"""
        with self.queue_lock:
            # Update status for all tasks in both queues
            with shared_tasks_lock:
                for task in self.normal_queue:
                    task_id = task["task_id"]
                    if task_id in shared_tasks:
                        # Clean up files
                        MapTaskQueueManager._clean_task_files(
                            shared_tasks[task_id].get("files", []))
                        shared_tasks[task_id] = {
                            **shared_tasks[task_id],
                            "status": ProcessingStatus.CANCELLED.value,
                            "files": []
                        }

                for task in self.preview_queue:
                    task_id = task["task_id"]
                    if task_id in shared_tasks:
                        # Clean up files
                        MapTaskQueueManager._clean_task_files(
                            shared_tasks[task_id].get("files", []))
                        shared_tasks[task_id] = {
                            **shared_tasks[task_id],
                            "status": ProcessingStatus.CANCELLED.value,
                            "files": []
                        }
            self.normal_queue = []
            self.preview_queue = []

    def get_queue_size(self, queue_type=None):
        """Get the number of tasks in the specified queue or total in all queues"""
        with self.queue_lock:
            if queue_type == QueueType.NORMAL:
                return len(self.normal_queue)
            elif queue_type == QueueType.PREVIEW:
                return len(self.preview_queue)
            else:
                return len(self.normal_queue) + len(self.preview_queue)

    def get_running_processes_count(self, queue_type=None):
        """Get the current number of running processes"""
        if queue_type == QueueType.NORMAL:
            return self.running_normal_processes.value
        elif queue_type == QueueType.PREVIEW:
            return self.running_preview_processes.value
        else:
            return self.running_normal_processes.value + self.running_preview_processes.value
