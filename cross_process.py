import os
from multiprocessing import Queue, Process

from cross_process_runnable import CrossProcessRunnable
from models import TaskResult, TaskRequest
from run_cross_process import run_cross_process


class CrossProcessCommunicator:
    def __init__(self, instance):
        self.instance = instance
        self.task_queue = Queue()
        self.response_queue = Queue()
        self.process: Process = None

    def start(self):
        self.process = Process(target=run_cross_process, args=(self.instance, self.task_queue, self.response_queue))
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


if __name__ == '__main__':
    print(os.getpid())
    c = CrossProcessCommunicator(CrossProcessRunnable())
    c.start()
    c.do_something()
    c.stop()
