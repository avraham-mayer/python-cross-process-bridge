from multiprocessing import Queue

from cross_process.instance_creator import InstanceCreator
from cross_process.models import TaskRequest, TaskResult


def run_cross_process(task_queue: Queue, response_queue: Queue, instance_generator: InstanceCreator):
    instance = None
    while True:
        task: TaskRequest = task_queue.get()
        if task.func_name == 'start' and instance is None:
            try:
                instance = instance_generator.generate()
            except Exception as e:
                response_queue.put(TaskResult(None, e))
                continue

            if hasattr(instance, 'start') and callable(getattr(instance, 'start')):
                instance.start(*task.args, **task.kwargs)

            response_queue.put(TaskResult(None, None))
            continue
        elif task.func_name == 'stop':
            if hasattr(instance, 'stop') and callable(getattr(instance, 'stop')):
                try:
                    instance.stop(*task.args, **task.kwargs)
                except Exception as e:
                    response_queue.put(TaskResult(None, e))
                    return

            response_queue.put(TaskResult(None, None))
            return

        if instance is None:
            continue

        retval = None
        exception = None
        try:
            retval = instance.__getattribute__(task.func_name)(*task.args, **task.kwargs)
        except Exception as e:
            exception = e

        response_queue.put(TaskResult(retval, exception))
