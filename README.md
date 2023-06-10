# Cross Process Bridge

This package is a utility for creating an instance of a class in a new process and seamlessly calling its functions from
the original process  

## When would I ever want to do that?
Good question, I'm glad you asked.  
Let's say you have a class, that changes the `cwd` of the program during the course of its actions. If you have another 
thread running, which needs a different `cwd`, they will interfere with each other because threads share a `cwd`  
  
Another example would be if you have a process running as root, which needs to do something risky that you wouldn't want
a privileged user doing, or just doesn't need high privileges. With this module you could call `os.setuid()` in the
child process without dropping privileges in the main process.
  
## So why wouldn't I just use multiprocessing?
The `multiprocessing` module allows running a python function in a separate process using
`multiprocessing.Process` like this:  
```python
process = multiprocessing.Process(target=func_to_run, args=(args, to, send))
process.start()
# do other things
process.join()
```

### why multiprocessing isn't enough 
The above example will run the function `func_to_run` with the given arguments. the program can then do other things and
wait for the process using `process.join()` when it needs to.  
However, it only runs the `func_to_run` and then exits.

## Cross Process Class
This module allows creating an instance of a class in one process and then seamlessly calling its functions from the 
main process

### Example
let's say I have a class `A` which has a method `a` which prints the pid of the process in which it is running
```python
class A:
    def a(self):
        print('a', os.getpid())
```

and let's further assume, that I didn't just create this class to check whether what I did worked, and say we just
really want to run an instance of this class in another process for completely unrelated reasons  
  
The module exports a class `CrossProcessBridge` which must be inherited from in order to run in another process  
  
If, for example I want to run an instance of the `A` class in a separate process:  
I will create a new class, in this case `B` which will inherit from both `A` and from `CrossProcessBridge`
  
**important** - the new class must inherit first from your class - `A` in this example - and then `CrossProcessBridge`  

```python
class B(A, CrossProcessBridge):
    pass
```
after creating an instance of `B` I will then call the `start()` method from the `CrossProcessBridge` class - this will
create another process, and in it create an instance of `A` **importantly, not of `B`**! it will create an instance of
the original `A` class  
I can now call any methods that exist in the `A` class on the `B` instance I have created, and they will be called in the
new process.  
when I am done I can call `stop()` which will stop the process

#### Complete example:

```python
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
```

### Pitfalls

#### Memory space
As with anything involving multiprocessing, a significant pitfall is separate memory spaces.  
for example:
```python
class A:
    def add_to_list(self, lst):
        lst.append('a')


class B(A, CrossProcessBridge):
    pass


def main():
    b = B()
    b.start()

    lst = []
    b.add_to_list(lst)
    print(lst)

    b.stop()


if __name__ == '__main__':
    main()
```

in this example the `A` class has a method `add_to_list` which gets a list and adds an `'a'` to it.  
the `print` in the line after the function call, will output an empty list because the lst object in memory in the main 
process is not the same list in the child process - it is copied into it when it is passed as a variable but changes to
it will not be reflected in the main process.  
The `multiprocessing.Manager` class can share simple objects including lists between processes:
```python
from multiprocessing import Manager

from cross_process_bridge import CrossProcessBridge


class A:
    def add_to_list(self, lst):
        lst.append('a')


class B(A, CrossProcessBridge):
    pass


def main():
    with B() as b:
        lst = Manager().list()
        b.add_to_list(lst)
        print(lst)


if __name__ == '__main__':
    main()
```
in this example, appending `'a'` to the list _is_ reflected in the main process because the list is a proxy object 
handled by `multiprocessing.Manager`

#### Method call-through
if your class has methods called `start` or `stop`, they will be called when starting and stopping the process - this is
to allow any setup and teardown you want to do. you _can_ pass parameters to the start and stop methods, but it is 
recommended that they have no parameters for simplicity and because when using the `with` keyword on the class, 
`start()` and `stop()` are called with no parameters


### Other usages

in addition to the classic usage above, the class can also be used as a context manager using the `with` keyword:
```python
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
```
when entering the `with` block the `start()` method will be called and when exiting, the `stop()` method will be called.