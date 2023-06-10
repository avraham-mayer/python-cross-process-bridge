import os

from cross_process.cross_process_runner import CrossProcessRunner
from cross_process.instance_creator import InstanceCreator


class CrossProcessExample:
    def start(self):
        print('starting', os.getpid())

    def stop(self):
        print('stopping', os.getpid())

    def do_something(self):
        print('doing something', os.getpid())


def create_instance() -> CrossProcessExample:
    return CrossProcessExample()


if __name__ == '__main__':
    instance_creator = InstanceCreator(create_instance)
    cross = CrossProcessRunner(instance_creator)

    print('calling process', os.getpid())
    cross.start()
    cross.do_something()
    cross.stop()
