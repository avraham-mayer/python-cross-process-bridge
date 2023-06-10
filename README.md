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
this will run the function `func_to_run` with the given arguments. the program can then do other things and wait for the
process using `process.join()` when it needs to  
  
however, even if the `func_to_run` creates an instance of a class, this does not allow calling function of that class
from the main process

## Cross Process Class
This module allows creating an instance of a class in one process and then seamlessly calling its functions from the 
main process

### example
```python

```