#!/usr/bin/env python
# encoding: utf-8
from environment import Environment
from utils import apply_op
from itertools import zip_longest
from parse import Parser
from token_stream import TokenStream
from input_stream import InputStream
from typing import Dict, Callable, Any
import time

Ast = Dict


def evaluate(ast: Ast, env: Environment, callback) -> None:
    type_ = ast['type']
    if type_ in {'num', 'str', 'bool'}:
        callback(ast['value'])
    elif type_ == 'var':
        callback(env.get(ast['value']))
    elif type_ == 'assign':
        if ast['left']['type'] != 'var':
            raise Exception(f"Cannot assign to {ast['left']}")
        evaluate(ast['right'], env, lambda right: callback(
            env.set(ast['left']['value'], right)))
    elif type_ == 'binary':
        evaluate(ast['left'], env, lambda left: evaluate(ast['right'], env, lambda right: callback(
            apply_op(ast['operator'], left, right))))
    elif type_ == 'lambda':
        callback(make_lambda(env, ast))
    elif type_ == 'if':
        def if_callback(cond):
            if cond is not False:
                evaluate(ast['then'], env, callback)
            elif 'else' in ast:
                evaluate(ast['else'], env, callback)
            else:
                callback(False)

        evaluate(ast['cond'], env, if_callback)
    elif type_ == 'let':
        def loop(env, i):
            if i < len(ast['vars']):
                var = ast['vars'][i]
                scope = env.extend()
                if var['def']:
                    def define_callback(value):
                        scope.define(var['name'], value)
                        loop(scope, i + 1)

                    evaluate(var['def'], env, define_callback)
                else:
                    scope.define(var['name'], False)
                    loop(scope, i + 1)
            else:
                evaluate(ast['body'], env, callback)

        loop(env, 0)
    elif type_ == 'prog':
        def loop(last, i):
            if i < len(ast['prog']):
                evaluate(ast['prog'][i], env, lambda value: loop(value, i + 1))
            else:
                callback(last)

        loop(False, 0)
    elif type_ == 'call':
        def call_callback(func):
            def loop(args, i):
                def arg_callback(arg):
                    args.append(arg)
                    loop(args, i + 1)

                if i < len(ast['args']):
                    evaluate(ast['args'][i], env, arg_callback)
                else:
                    func(*args)

            loop([callback], 0)

        evaluate(ast['func'], env, call_callback)
    else:
        raise Exception(f"I don'tt know how to evaluate {ast['type']}")


def make_lambda(env: Environment, ast: Ast) -> Callable:
    def lambda_function(callback, *args):
        names = ast['vars']
        assert len(names) >= len(args)
        scope = env.extend()
        for name, value in zip_longest(names, args, fillvalue=False):
            scope.define(name, value)
        evaluate(ast['body'], scope, callback)

    if ast['name']:
        env = env.extend()
        env.define(ast['name'], lambda_function)
    return lambda_function


def main():
    # code = "sum = lambda(x, y) x + y; print(sum(2, 3));"
    code = """
    fib = λ(n) if n < 2 then n else fib(n - 1) + fib(n - 2);
    time( λ() println(fib(6)) );
    """
    # code = """
    # fib = λ(n) if n < 2 then n else fib(n - 1) + fib(n - 2);
    # println(fib(8));
    # """
    parser = Parser(TokenStream(InputStream(code)))
    global_env = Environment()

    def custom_print(callback, txt):
        print(txt, end=' ')
        callback(False)

    def custom_println(callback, txt):
        print(txt, end='\n')
        callback(False)

    def timing(callback, func):
        start_time = time.time()

        def timing_callback(result):
            end_time = time.time()
            print(f"Time: {(end_time - start_time) * 1000}ms", end='\n')
            callback(result)
        func(timing_callback)
    global_env.define("print", custom_print)
    global_env.define("time", timing)
    global_env.define("println", custom_println)
    evaluate(parser(), global_env, lambda result: result)


if __name__ == "__main__":
    main()
