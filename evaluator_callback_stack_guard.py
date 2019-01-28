#!/usr/bin/env python
# encoding: utf-8
# !/usr/bin/env python
# encoding: utf-8
from environment import Environment
from utils import apply_op
from itertools import zip_longest

STACKLEN = 0


class Continuation(Exception):
    def __init__(self, f, args):
        super(Continuation, self).__init__(f, args)
        self.f = f
        self.args = args


def GUARD(f, args):
    global STACKLEN
    STACKLEN -= 1
    if STACKLEN < 0:
        raise Continuation(f, args)


def Execute(f, args):
    global STACKLEN
    while True:
        STACKLEN = 200
        # print(f, args)
        try:
            return f(*args)
        except Continuation as e:
            f = e.f
            args = e.args


def evaluate(ast: dict, env: Environment, callback):
    GUARD(evaluate, [ast, env, callback])
    type = ast['type']
    if type in {'num', 'str', 'bool'}:
        callback(ast['value'])
    elif type == 'var':
        callback(env.get(ast['value']))
    elif type == 'assign':
        if ast['left']['type'] != 'var':
            raise Exception(f"Cannot assign to {ast['left']}")

        def assign_callback(right):
            GUARD(assign_callback, [right])
            callback(env.set(ast['left']['value'], right))

        evaluate(ast['right'], env, assign_callback)
    elif type == 'binary':
        def left_callback(left):
            GUARD(left_callback, [left])

            def right_callback(right):
                GUARD(right_callback, [right])
                callback(apply_op(ast['operator'], left, right))

            evaluate(ast['right'], env, right_callback)

        evaluate(ast['left'], env, left_callback)
    elif type == 'lambda':
        callback(make_lambda(env, ast))
    elif type == 'if':
        def if_callback(cond):
            GUARD(if_callback, [cond])
            if cond is not False:
                evaluate(ast['then'], env, callback)
            elif 'else' in ast:
                evaluate(ast['else'], env, callback)
            else:
                callback(False)

        evaluate(ast['cond'], env, if_callback)
    elif type == 'let':
        def loop(env, i):
            GUARD(loop, [env, i])
            if i < len(ast['vars']):
                var = ast['vars'][i]
                scope = env.extend()
                if var['def']:
                    def define_callback(value):
                        GUARD(define_callback, [value])
                        scope.define(var['name'], value)
                        loop(scope, i + 1)

                    evaluate(var['def'], env, define_callback)
                else:
                    scope.define(var['name'], False)
                    loop(scope, i + 1)
            else:
                evaluate(ast['body'], env, callback)

        loop(env, 0)
    elif type == 'prog':
        def loop(last, i):
            GUARD(loop, [last, i])
            if i < len(ast['prog']):
                def expression_callback(value):
                    GUARD(expression_callback, [value])
                    loop(value, i + 1)

                evaluate(ast['prog'][i], env, expression_callback)
            else:
                callback(last)

        loop(False, 0)
    elif type == 'call':
        def call_callback(func):
            GUARD(call_callback, [func])

            def loop(args, i):
                # print(f"call loop: {args} {i}")
                GUARD(loop, [args, i])

                def arg_callback(arg):
                    GUARD(arg_callback, [arg])
                    args.append(arg)
                    loop(args, i + 1)

                if i < len(ast['args']):
                    evaluate(ast['args'][i], env, arg_callback)
                else:
                    func(*args)

            loop([callback], 0)

        evaluate(ast['func'], env, call_callback)
    else:
        raise Exception("I don'tt know how to evaluate " + ast['type'])


def make_lambda(env, exp):
    def lambda_function(callback, *args):
        GUARD(lambda_function, [callback, *args])
        scope = env.extend()
        names = exp['vars']
        assert len(names) >= len(args)
        for name, value in zip_longest(names, args, fillvalue=False):
            scope.define(name, value)
        evaluate(exp['body'], scope, callback)

    if exp['name']:
        env = env.extend()
        env.define(exp['name'], lambda_function)
    return lambda_function


# if __name__ == '__main__':
#     from input_stream import InputStream
#     from token_stream import TokenStream
#     from parse import Parser
#     from environment import Environment
#
#
#     def println(callback, txt):
#         print(txt)
#         callback(False)
#
#
#     def time(callback, fn):
#         from datetime import datetime
#         t1 = datetime.now()
#
#         def time_callback(value):
#             t2 = datetime.now()
#             print(f"Time: {t2 - t1} seconds")
#             print(callback)
#             callback(value)
#
#         fn(time_callback)
#
#
#     globalEnv = Environment()
#     globalEnv.define('time', time)
#     globalEnv.define('println', println)
#     code = "fibJS = lambda (n) if n < 2 then n else fibJS(n - 1) + fibJS(n - 2);fibJS(20)"
#     code = "fib = λ(n) if n < 2 then n else fib(n - 1) + fib(n - 2); time( λ() println(fib(20)) );"
#     code = """sum = λ(n, ret) if n == 0 then ret else sum(n - 1, ret + n);
#     # compute 1 + 2 + ... + 50000
#     time( λ() println(sum(50000, 0)) );"""
#     ast = Parser(TokenStream(InputStream(code)))()
#     Execute(evaluate, [ast, globalEnv, lambda result: print(f"*** Result: {result}")])
