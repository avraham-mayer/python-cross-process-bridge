from multiprocessing import Queue
from typing import Tuple, Any

from cross_process_bridge.instance_creator import InstanceCreator
from cross_process_bridge.models import TaskRequest, TaskResult


class ChildProcessBridge:
    def __init__(self, task_queue: Queue, response_queue: Queue, instance_creator: InstanceCreator):
        self.task_queue = task_queue
        self.response_queue = response_queue
        self.instance_creator = instance_creator
        self.instance = None

    def create_instance(self, task: TaskRequest) -> TaskResult:
        try:
            retval = None
            self.instance = self.instance_creator.create()
            if hasattr(self.instance, 'start') and callable(getattr(self.instance, 'start')):
                retval = self.instance.start(*task.args, **task.kwargs)
            return TaskResult(retval, None)
        except Exception as e:
            return TaskResult(None, e)

    def run_method(self, task) -> TaskResult:
        retval = None
        exception = None
        try:
            retval = self.instance.__getattribute__(task.func_name)(*task.args, **task.kwargs)
        except Exception as e:
            exception = e
        return TaskResult(retval, exception)

    def run(self):
        while True:
            task: TaskRequest = self.task_queue.get()
            if task.func_name == 'start' and self.instance is None:
                result = self.create_instance(task)
                self.response_queue.put(result)
                continue
            elif task.func_name == 'stop':
                if hasattr(self.instance, 'stop') and callable(getattr(self.instance, 'stop')):
                    result = self.run_method(task)
                else:
                    result = TaskResult(None, None)
                self.response_queue.put(result)
                return

            if self.instance is None:
                continue

            result = self.run_method(task)
            self.response_queue.put(result)


def run_cross_process(task_queue: Queue, response_queue: Queue, instance_creator: InstanceCreator):
    bridge = ChildProcessBridge(task_queue, response_queue, instance_creator)
    bridge.run()
