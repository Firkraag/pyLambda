#!/usr/bin/env python
# encoding: utf-8
from environment import Environment
from utils import apply_op
from itertools import zip_longest


def evaluate_callback(exp: dict, env: Environment, callback):
    type = exp['type']
    if type in {'num', 'str', 'bool'}:
        callback(exp['value'])
    elif type == 'var':
        callback(env.get(exp['value']))
    elif type == 'assign':
        if exp['left']['type'] != 'var':
            raise Exception(f"Cannot assign to {exp['left']}")
        evaluate_callback(exp['right'], env, lambda right: callback(env.set(exp['left']['value'], right)))
    elif type == 'binary':
        evaluate_callback(exp['left'], env, lambda left: evaluate_callback(exp['right'], env, lambda right: callback(
            apply_op(exp['operator'], left, right))))
        # return apply_op(exp['operator'], evaluate(exp['left'], env), evaluate(exp['right'], env))
    elif type == 'lambda':
        callback(make_lambda_callback(env, exp))
    elif type == 'if':
        def if_callback(cond):
            if cond is not False:
                evaluate_callback(exp['then'], env, callback)
            elif 'else' in exp:
                evaluate_callback(exp['else'], env, callback)
            else:
                callback(False)

        evaluate_callback(exp['cond'], env, if_callback)
    elif type == 'let':
        scope = env.extend()
        for var in exp['vars']:
            # scope = env.extend()
            print(var)
            if var['def']:
                evaluate_callback(var['def'], env, lambda value: scope.define(var['name'], value))
            else:
                scope.define(var['name'], False)
            # scope.define(var['name'], evaluate(var['def'], env) if var['def'] else False)
            # env = scope
        print('aaaa')
        evaluate_callback(exp['body'], scope, callback)
    elif type == 'prog':
        def prog_callback(value):
            nonlocal val
            val = value

        val = False
        for expression in exp['prog']:
            evaluate_callback(expression, env, prog_callback)
        callback(val)
    elif type == 'call':
        def call_callback(func):
            args = []
            for arg in exp['args']:
                evaluate_callback(arg, env, lambda value: args.append(value))
            func(callback, *args)

        evaluate_callback(exp['func'], env, call_callback)
    else:
        raise Exception("I don'tt know how to evaluate " + exp['type'])


def make_lambda_callback(env, exp):
    def lambda_function(callback, *args):
        scope = env.extend()
        names = exp['vars']
        args = args[:len(names)]
        for name, value in zip_longest(names, args, fillvalue=False):
            scope.define(name, value)
        evaluate_callback(exp['body'], scope, callback)

    if exp['name']:
        env = env.extend()
        env.define(exp['name'], lambda_function)
    return lambda_function
