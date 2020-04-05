import time
from functools import partial
from typing import Callable, Any


def _fib_py(number):
    if number < 2:
        return number
    return _fib_py(number - 1) + _fib_py(number - 2)


def _timing(func: Callable[[], Any]):
    start_time = time.time()
    result = func()
    end_time = time.time()
    print(f"Time: {(end_time - start_time) * 1000}ms", end='\n')
    return result


def _halt():
    pass


primitive = {
    'print': partial(print, end=' '),
    'println': partial(print, end='\n'),
    'fibPY': _fib_py,
    'time': _timing,
    'halt': _halt,
}
