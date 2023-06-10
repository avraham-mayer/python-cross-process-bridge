class TaskResult:
    def __init__(self, retval, exception):
        self.retval = retval
        self.exception = exception


class TaskRequest:
    def __init__(self, func_name, *args, **kwargs):
        self.func_name = func_name
        self.args = args
        self.kwargs = kwargs
