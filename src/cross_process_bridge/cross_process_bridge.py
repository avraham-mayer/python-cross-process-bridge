from multiprocessing import Queue, Process
from typing import Optional

from cross_process_bridge.child_process_bridge import run_cross_process
from cross_process_bridge.instance_creator import InstanceCreator
from cross_process_bridge.models import TaskResult, TaskRequest


class CrossProcessMetaclass(type):
    @classmethod
    def _insert_wrapper_functions(cls, dct, base):
        for key, value in base.__dict__.items():
            if callable(value) and key not in ('__init__', 'start', 'stop'):
                dct[key] = CrossProcessBridge.create_cross_process_function(item=key)
        for b in base.__bases__:
            if b is not object:
                cls._insert_wrapper_functions(dct, b)

    def __new__(cls, name, bases, dct):
        if name == 'CrossProcessBridge':
            return super().__new__(cls, name, bases, dct)

        if bases[1] is not CrossProcessBridge:
            raise Exception('must inherit from CrossProcessBridge second')
        if len(bases) != 2:
            raise Exception('must have exactly one base other than CrossProcessBridge')

        real_base = bases[0]
        cls._insert_wrapper_functions(dct, real_base)
        dct['__getattr__'] = CrossProcessBridge.create_cross_process_function('__getattribute__')
        custom_setattr = CrossProcessBridge.create_cross_process_function('__setattr__')
        dct['custom_setattr'] = custom_setattr

        dct['real_base'] = real_base
        return super().__new__(cls, name, (CrossProcessBridge, real_base), dct)


class CrossProcessBridge(metaclass=CrossProcessMetaclass):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.task_queue = Queue()
        self.response_queue = Queue()
        self.process: Optional[Process] = None

    def start(self, *args, **kwargs):
        if self.process is None or not self.process.is_alive():
            instance_creator = InstanceCreator(self.real_base, *self.args, **self.kwargs)
            self.process = Process(target=run_cross_process,
                                   args=(self.task_queue, self.response_queue, instance_creator))
            self.process.start()
        self.task_queue.put(TaskRequest('start', *args, **kwargs))
        result: TaskResult = self.response_queue.get()
        if result.exception is not None:
            raise result.exception

    def stop(self, *args, **kwargs):
        if self.process is not None and self.process.is_alive():
            self.task_queue.put(TaskRequest('stop', *args, **kwargs))
            self.response_queue.get()
            self.process.join()
            self.process = None

    @staticmethod
    def create_cross_process_function(item):
        def cross_process_function(self: CrossProcessBridge, *args, **kwargs):
            self.task_queue.put(TaskRequest(item, *args, **kwargs))
            result: TaskResult = self.response_queue.get()
            if result.exception is not None:
                raise result.exception
            return result.retval

        return cross_process_function

    def __del__(self):
        self.stop()

    def __setattr__(self, key, value):
        if key in self.__dict__ or 'process' not in self.__dict__ or self.process is None or not self.process.is_alive():
            return super().__setattr__(key, value)

        return self.custom_setattr(key, value)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
