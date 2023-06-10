import os


class CrossProcessRunnable:
    def start(self):
        print('starting', os.getpid())

    def stop(self):
        print('stopping', os.getpid())

    def do_something(self):
        print('doing something', os.getpid())
