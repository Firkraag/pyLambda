"""
CPS-style primitive
"""
from typing import Callable, Any
import time


def _sleep(callback: Callable, seconds: float):
    time.sleep(seconds)
    callback(False)


def _custom_print(callback, txt):
    print(txt, end=' ')
    callback(False)


def _custom_println(callback, txt):
    print(txt, end='\n')
    callback(False)


def _timing(callback, func):
    start_time = time.time()

    def timing_callback(result):
        end_time = time.time()
        print(f"Time: {(end_time - start_time) * 1000}ms", end='\n')
        callback(result)
    func(timing_callback)


def _halt(callback):
    pass


def _twice(callback: Callable[[Any], Any], a, b):
    callback(a)
    callback(b)


primitive = {
    'sleep': _sleep,
    'print': _custom_print,
    'println': _custom_println,
    'time': _timing,
    'halt': _halt,
    'twice': _twice,
}
