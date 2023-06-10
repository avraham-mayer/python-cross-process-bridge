import os

from cross_process_bridge import CrossProcessBridge


class A:
    @staticmethod
    def a():
        print('a', os.getpid())

    def __str__(self):
        return f'A.__str__ {os.getpid()}'


class B(A):
    def __init__(self, thing):
        self.thing = thing
        print(f'B __init__ {thing}', os.getpid())

    @staticmethod
    def b():
        print('b', os.getpid())

    def __bool__(self):
        print('__bool__', os.getpid())
        return self.thing == 'b'


class C(B, CrossProcessBridge):
    pass


def main():
    print('original process', os.getpid())
    c = C('b')
    c.start()
    c.a()
    c.b()
    print(bool(c))
    print(c)
    c.stop()


if __name__ == '__main__':
    main()
