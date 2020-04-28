"""
CPS-style primitive
"""
from typing import Callable, Any
import time


def _fibpy(callback: Callable, number: int):
    def _fibpy_aux(number: int) -> int:
        if number < 2:
            return number
        return _fibpy_aux(number - 1) + _fibpy_aux(number - 2)
    callback(_fibpy_aux(number))




def _sleep(callback: Callable, seconds: float):
    time.sleep(seconds)
    callback(False)


def _custom_print(callback, txt):
    print(txt, end=' ')
    callback(False)


def _custom_println(callback, txt):
    print(txt, end='\n')
    callback(False)


def _timing(callback, func, *args):
    start_time = time.time()

    def timing_callback(result):
        end_time = time.time()
        print(f"Time: {(end_time - start_time) * 1000}ms", end='\n')
        callback(result)
    func(timing_callback, *args)

# pylint: disable=unused-argument


def _halt(callback):
    pass


def _twice(callback: Callable[[Any], Any], arg1, arg2):
    callback(arg1)
    callback(arg2)


def _call_cc(callback: Callable, func: Callable):
    func(callback, lambda discard, ret: callback(ret))


# def _with_yield(callback: Callable, yield_func: Callable):
#     yield_func(callback, lambda cb, ret: callback(ret), )
#     func(callback, lambda discard, ret: callback(ret))


primitive = {
    'sleep': _sleep,
    'print': _custom_print,
    'println': _custom_println,
    'time': _timing,
    'halt': _halt,
    'twice': _twice,
    'CallCC': _call_cc,
    'fibpy': _fibpy,
}
