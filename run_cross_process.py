from multiprocessing import Queue

from cross_process_runnable import CrossProcessRunnable
from models import TaskRequest, TaskResult


def run_cross_process(instance: CrossProcessRunnable, task_queue: Queue, response_queue: Queue):
    while True:
        task: TaskRequest = task_queue.get()
        if task.func_name == 'start':
            instance.start()
        elif task.func_name == 'stop':
            instance.stop()
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
