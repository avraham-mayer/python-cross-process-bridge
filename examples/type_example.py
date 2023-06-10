import os

from cross_process.cross_process_runner import CrossProcessRunner


class CrossProcessExample:
    def start(self):
        print('starting', os.getpid())

    def stop(self):
        print('stopping', os.getpid())

    def do_something(self):
        print('doing something', os.getpid())


if __name__ == '__main__':
    cross: CrossProcessExample = CrossProcessRunner.type(CrossProcessExample)

    print('calling process', os.getpid())
    cross.start()
    cross.do_something()
    cross.stop()
