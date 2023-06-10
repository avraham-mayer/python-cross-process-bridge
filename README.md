# Cross Process

This package is a utility for creating an instance of a class in a new process and seamlessly calling its functions from
the original process  
  
## Background
### multiprocessing
let's say I have a class that needs to do something that affects the whole process - for example changing the working 
directory, using setuid, or any other action that cannot be done in a thread without affecting the rest of the process  

The module `multiprocessing` module allows running a python function in a separate process using
`multiprocessing.Process` like this:  
```python
process = multiprocessing.Process(target=func_to_run, args=(args, to, send))
process.start()
# do other things
process.join()
```

### why multiprocessing isn't enough 
The above example will run the function `func_to_run` with the given arguments. the program can then do other things and
wait for the process using `process.join()` when it needs to  
  
however, even if the `func_to_run` creates an instance of a class, this does not allow calling functions of that class
from the main process - it only runs the `func_to_run` and then exits

## Cross Process Class
This module allows creating an instance of a class in one process and then seamlessly calling its functions from the 
main process

### Example
let's say i have a class `A` which has a method `a` which prints the pid of the process in which it is running
```python
class A:
    def a(self):
        print('a', os.getpid())
```

and let's further assume, that I didn't just create this class to check whether what i did worked, and say we just
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
I can now call any methods that exist in the `A` class on the `B` instance I have created and they will be called in the
new process.  
when I am done i can call `stop()` which will stop the process

#### Complete example:

```python
import os
from cross_process_bridge.cross_process_bridge import CrossProcessBridge


class A:
    def a(self):
        print('a', os.getpid())


class B(A, CrossProcessBridge):
    pass


if __name__ == '__main__':
    pid = os.getpid()
    print(pid)  # print the pid of the original process
    b = B()  # create the bridge instance
    b.start()  # start the process and create an instance in it
    b.a()  # call the `a()` function - will print a different pid
    b.stop()  # stop the process
```
