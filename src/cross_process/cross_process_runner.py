from multiprocessing import Queue, Process
from typing import Type

from cross_process.instance_creator import InstanceCreator
from cross_process.models import TaskResult, TaskRequest
from cross_process.run_cross_process import run_cross_process


class CrossProcessRunner:
    def __init__(self, instance_creator: InstanceCreator):
        self.instance_creator = instance_creator
        self.task_queue = Queue()
        self.response_queue = Queue()
        self.process: Process = None

    @classmethod
    def type(cls, instance_type: Type, *args, **kwargs):
        return cls(InstanceCreator(instance_type, *args, **kwargs))

    def start(self):
        self.process = Process(target=run_cross_process,
                               args=(self.task_queue, self.response_queue, self.instance_creator))
        self.process.start()
        self.task_queue.put(TaskRequest('start'))
        self.response_queue.get()

    def stop(self):
        self.task_queue.put(TaskRequest('stop'))
        self.response_queue.get()
        self.process.join()

    def __getattr__(self, item):
        def cross_process_function(*args, **kwargs):
            self.task_queue.put(TaskRequest(item, *args, **kwargs))
            result: TaskResult = self.response_queue.get()
            if result.exception is not None:
                raise result.exception
            return result.retval

        return cross_process_function
