import os
from cross_process_bridge import CrossProcessBridge


class A:
    def a(self):
        print('a', os.getpid())


class B(A, CrossProcessBridge):
    pass


if __name__ == '__main__':
    pid = os.getpid()
    print(pid)  # print the pid of the original process
    b = B()     # create the bridge instance
    b.start()   # start the process and create an instance in it
    b.a()       # call the `a()` function - will print a different pid
    b.stop()    # stop the process
