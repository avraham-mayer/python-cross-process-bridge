from typing import Callable


class InstanceCreator:
    def __init__(self, instance_function: Callable, *instance_args, **instance_kwargs):
        self.instance_function = instance_function
        self.instance_args = instance_args
        self.instance_kwargs = instance_kwargs

    def generate(self):
        return self.instance_function(*self.instance_args, **self.instance_kwargs)
