import os

from cross_process import CrossProcessBridge


class C:
    def c(self):
        print('c', os.getpid())


class A(C):
    def __init__(self, thing):
        self.thing = thing
        print(f'A __init__ {thing}', os.getpid())

    def a(self):
        print('a', os.getpid())

    def __bool__(self):
        print('__bool__', os.getpid())
        return self.thing == 'a'


class B(A, CrossProcessBridge):
    pass


if __name__ == '__main__':
    print('original process', os.getpid())
    b = B('a')
    b.start()
    b.a()
    # b.c()
    print(bool(b))
    b.stop()
