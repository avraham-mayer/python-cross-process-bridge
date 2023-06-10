import os

from cross_process.cross_process import CrossProcess


class A:
    def __init__(self, thing):
        self.thing = thing
        print(f'A __init__ {thing}', os.getpid())

    def a(self):
        print('a', os.getpid())


class B(A, CrossProcess):
    pass


if __name__ == '__main__':
    print('original process', os.getpid())
    b = B()
    b.start()
    b.a()
    b.stop()
