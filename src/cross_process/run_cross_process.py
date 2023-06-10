from multiprocessing import Queue
from typing import Tuple, Type

from cross_process.instance_creator import InstanceCreator
from cross_process.models import TaskRequest, TaskResult


def create_instance(instance_creator: InstanceCreator, task: TaskRequest) -> Tuple[..., TaskResult]:
    try:
        retval = None
        instance = instance_creator.create()
        if hasattr(instance, 'start') and callable(getattr(instance, 'start')):
            retval = instance.start(*task.args, **task.kwargs)
        return instance, TaskResult(retval, None)
    except Exception as e:
        return None, TaskResult(None, e)


def run_method(instance, task) -> TaskResult:
    retval = None
    exception = None
    try:
        retval = instance.__getattribute__(task.func_name)(*task.args, **task.kwargs)
    except Exception as e:
        exception = e
    return TaskResult(retval, exception)


def run_cross_process(task_queue: Queue, response_queue: Queue, instance_creator: InstanceCreator):
    instance = None
    while True:
        task: TaskRequest = task_queue.get()
        if task.func_name == 'start' and instance is None:
            instance, result = create_instance(instance_creator, task)
            response_queue.put(result)
            continue
        elif task.func_name == 'stop':
            if hasattr(instance, 'stop') and callable(getattr(instance, 'stop')):
                result = run_method(instance, task)
                response_queue.put(result)
            return

        if instance is None:
            continue

        result = run_method(instance, task)
        response_queue.put(result)
