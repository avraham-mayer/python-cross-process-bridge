import os
from cross_process_bridge import CrossProcessBridge


class A:
    @staticmethod
    def a():
        print('a', os.getpid())


class B(A, CrossProcessBridge):
    pass


def main():
    pid = os.getpid()
    print(pid)
    with B() as b:
        b.a()


if __name__ == '__main__':
    main()
