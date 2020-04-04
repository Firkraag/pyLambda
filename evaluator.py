#!/usr/bin/env python
# encoding: utf-8
import time
from functools import partial
from itertools import zip_longest
from typing import Any, Dict, Callable
import sys

from environment import Environment
from input_stream import InputStream
from parse import Parser
from token_stream import TokenStream
from utils import apply_op


def evaluate(ast: Dict, env: Environment) -> Any:
    """
    For num, str, bool nodes, return their value;
    variable are fetched from the environment;
    For assignment, we need to check if the left side is a "var" token(if not,
    throw an error;we don't support assignment to anything else for now),
    then we use env.set to set the value, note that the value needs to
    be computed first by calling evaluate recursively.
    And in any environment except global environment,
    the assigned variable must be defined previously in some environment.
    Currently, variables are defined only when an lambda function is called or
    an let node is evaluated.
    That means we cannot define a new variable inside lambda function body.
    A binary node applies node operator to node left operand and right operand.
    A lambda node will actually result in a Python closure,
    so it will be callable from Python just like an ordinary function.
    For a call node we need to call a function. First we evaluate the func,
    which should return a normal Python function,
    then we evaluate the args and apply that function.
    Evaluating an "if" node is simple: first evaluate the condition.
    If it's not False then evaluate the "then" branch and return its value.
    Otherwise, evaluate the "else" branch, if present, or return False
    A "prog" is a sequence of expressions. We just evaluate them in order and
    return the value of the last one.
    For am empty sequence, the return value is initialized to False.
    A named let of a form like 'let foo(var = value) body' is equivalent to
    '(lambda foo(var) body)(value)'

    :param ast:
    :param env:
    :return:
    """
    type_ = ast['type']
    if type_ in {'num', 'str', 'bool'}:
        return ast['value']
    if type_ == 'var':
        return env.get(ast['value'])
    if type_ == 'assign':
        left = ast['left']
        if left['type'] != 'var':
            raise Exception(f"Cannot assign to {ast['left']}")
        return env.set(left['value'], evaluate(ast['right'], env))
    if type_ == 'binary':
        return apply_op(ast['operator'], evaluate(ast['left'], env),
                        evaluate(ast['right'], env))
    if type_ == 'lambda':
        return make_lambda(env, ast)
    if type_ == 'if':
        cond = evaluate(ast['cond'], env)
        if cond is not False:
            return evaluate(ast['then'], env)
        if 'else' in ast:
            return evaluate(ast['else'], env)
        return False
    if type_ == 'prog':
        result = False
        for expr in ast['prog']:
            result = evaluate(expr, env)
        return result
    if type_ == 'call':
        func = evaluate(ast['func'], env)
        return func(*[evaluate(arg, env) for arg in ast['args']])
    if type_ == 'let':
        for var in ast['vars']:
            scope = env.extend()
            # if an arg is not assigned some value,
            # then False is assigned to the arg by the evaluator.
            scope.define(var['name'],
                         evaluate(var['def'], env) if var['def'] else False)
            env = scope
        return evaluate(ast['body'], env)
    raise Exception(f"I don't know how to evaluate {ast['type']}")


def make_lambda(env: Environment, ast: dict) -> Callable:
    def lambda_function(*args):
        names = ast['vars']
        assert len(names) >= len(args)
        scope = env.extend()
        for name, value in zip_longest(names, args, fillvalue=False):
            scope.define(name, value)
        return evaluate(ast['body'], scope)

    if ast['name']:
        env = env.extend()
        env.define(ast['name'], lambda_function)

    return lambda_function


def main():
    global_env = Environment()
    global_env.define("print", partial(print, end=' '))
    global_env.define("println", partial(print, end='\n'))

    def fib_py(number):
        if number < 2:
            return number
        return fib_py(number - 1) + fib_py(number - 2)

    global_env.define('fibPY', fib_py)

    def timing(func: Callable[[], Any]):
        start_time = time.time()
        result = func()
        end_time = time.time()
        print(f"Time: {(end_time - start_time) * 1000}ms", end='\n')
        return result

    global_env.define("time", timing)
    lambda_file_path = sys.argv[1]
    with open(lambda_file_path) as file:
        code = file.read()
        parser = Parser(TokenStream(InputStream(code)))
        evaluate(parser(), global_env)


if __name__ == '__main__':
    main()
#     code = """
#     cons = λ(a, b) λ(f) f(a, b);
# car = λ(cell) cell(λ(a, b) a);
# cdr = λ(cell) cell(λ(a, b) b);
# NIL = λ(f) f(NIL, NIL);
#     foreach = λ(list, f)
#             if list != NIL {
#               f(car(list));
#               foreach(cdr(list), f);
#             };
#     range = λ(a, b)
#           if a <= b then cons(a, range(a + 1, b))
#                     else NIL;
#
# # print the squares of 1..8
# foreach(range(1, 8), λ(x) println(x * x));
# """
# code = "sum = lambda(x, y) x + y; print(sum(2, 3));"
