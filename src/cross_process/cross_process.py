from multiprocessing import Queue, Process

from cross_process.instance_creator import InstanceCreator
from cross_process.models import TaskResult, TaskRequest
from cross_process.run_cross_process import run_cross_process


class CrossProcessMetaclass(type):

    def __new__(cls, name, bases, dct):
        if name == 'CrossProcess':
            return super().__new__(cls, name, bases, dct)

        if bases[1] is not CrossProcess:
            raise Exception('must inherit from CrossProcess second')
        if len(bases) != 2:
            raise Exception('must have exactly one base other than CrossProcess')

        real_base = bases[0]
        for key, value in real_base.__dict__.items():
            if callable(value) and key not in ('__init__', 'start', 'stop'):
                dct[key] = CrossProcess.create_cross_process_function(item=key)

        dct['real_base'] = real_base
        return super().__new__(cls, name, (CrossProcess, real_base), dct)


class CrossProcess(metaclass=CrossProcessMetaclass):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.task_queue = Queue()
        self.response_queue = Queue()
        self.process: Process = None

    def start(self, *args, **kwargs):
        if self.process is None or not self.process.is_alive():
            instance_creator = InstanceCreator(self.real_base, *self.args, **self.kwargs)
            self.process = Process(target=run_cross_process,
                                   args=(self.task_queue, self.response_queue, instance_creator))
            self.process.start()
        self.task_queue.put(TaskRequest('start', *args, **kwargs))
        self.response_queue.get()

    def stop(self, *args, **kwargs):
        if self.process is not None and self.process.is_alive():
            self.task_queue.put(TaskRequest('stop', *args, **kwargs))
            self.response_queue.get()
            self.process.join()
            self.process = None

    @staticmethod
    def create_cross_process_function(item):
        def cross_process_function(self: CrossProcess, *args, **kwargs):
            self.task_queue.put(TaskRequest(item, *args, **kwargs))
            result: TaskResult = self.response_queue.get()
            if result.exception is not None:
                raise result.exception
            return result.retval

        return cross_process_function
