#!/usr/bin/env python
# encoding: utf-8
from environment import Environment
from utils import apply_op
from itertools import zip_longest


def evaluate(ast: dict, env: Environment, callback):
    type = ast['type']
    if type in {'num', 'str', 'bool'}:
        callback(ast['value'])
    elif type == 'var':
        callback(env.get(ast['value']))
    elif type == 'assign':
        if ast['left']['type'] != 'var':
            raise Exception(f"Cannot assign to {ast['left']}")
        evaluate(ast['right'], env, lambda right: callback(env.set(ast['left']['value'], right)))
    elif type == 'binary':
        evaluate(ast['left'], env, lambda left: evaluate(ast['right'], env, lambda right: callback(
            apply_op(ast['operator'], left, right))))
    elif type == 'lambda':
        callback(make_lambda(env, ast))
    elif type == 'if':
        def if_callback(cond):
            if cond is not False:
                evaluate(ast['then'], env, callback)
            elif 'else' in ast:
                evaluate(ast['else'], env, callback)
            else:
                callback(False)

        evaluate(ast['cond'], env, if_callback)
    elif type == 'let':
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
    elif type == 'prog':
        def loop(last, i):
            if i < len(ast['prog']):
                evaluate(ast['prog'][i], env, lambda value: loop(value, i + 1))
            else:
                callback(last)
        loop(False, 0)
    elif type == 'call':
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
        raise Exception("I don'tt know how to evaluate " + ast['type'])


def make_lambda(env, exp):
    def lambda_function(callback, *args):
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
