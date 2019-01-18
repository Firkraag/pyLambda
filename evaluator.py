#!/usr/bin/env python
# encoding: utf-8
from itertools import zip_longest


class Environment(object):
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def extend(self):
        return Environment(self)

    def lookup(self, name: str):
        scope = self
        while scope:
            if name in scope.vars:
                return scope
            scope = scope.parent

    def define(self, name, value):
        self.vars[name] = value

    def get(self, name):
        scope = self
        while scope:
            if name in scope.vars:
                return scope.vars[name]
            scope = scope.parent
        raise Exception(f"Undefined variable {name}")

    def set(self, name: str, value: object) -> object:
        scope = self.lookup(name)
        if scope:
            scope.vars[name] = value
        elif self.parent:
            raise Exception(f"Undefined variable {name}")
        else:
            self.vars[name] = value
            return value


def evaluate(exp: dict, env: Environment, callback):
    type = exp['type']
    if type in {'num', 'str', 'bool'}:
        callback(exp['value'])
    elif type == 'var':
        callback(env.get(exp['value']))
    elif type == 'assign':
        if exp['left']['type'] != 'var':
            raise Exception(f"Cannot assign to {exp['left']}")
        evaluate(exp['right'], env, lambda right: callback(env.set(exp['left']['value'], right)))
    elif type == 'binary':
        evaluate(exp['left'], env, lambda left: evaluate(exp['right'], env, lambda right: callback(
            apply_op(exp['operator'], left, right))))
        # return apply_op(exp['operator'], evaluate(exp['left'], env), evaluate(exp['right'], env))
    elif type == 'lambda':
        callback(make_lambda(env, exp))
    elif type == 'if':
        def if_callback(cond):
            if cond is not False:
                evaluate(exp['then'], env, callback)
            elif 'else' in exp:
                evaluate(exp['else'], env, callback)
            else:
                callback(False)

        evaluate(exp['cond'], env, if_callback)
    elif type == 'let':
        scope = env.extend()
        for var in exp['vars']:
            # scope = env.extend()
            print(var)
            if var['def']:
                evaluate(var['def'], env, lambda value: scope.define(var['name'], value))
            else:
                scope.define(var['name'], False)
            # scope.define(var['name'], evaluate(var['def'], env) if var['def'] else False)
            # env = scope
        print('aaaa')
        evaluate(exp['body'], scope, callback)
    elif type == 'prog':
        def prog_callback(value):
            nonlocal val
            val = value

        val = False
        for expression in exp['prog']:
            evaluate(expression, env, prog_callback)
        callback(val)
    elif type == 'call':
        def call_callback(func):
            args = []
            for arg in exp['args']:
                evaluate(arg, env, lambda value: args.append(value))
            func(callback, *args)

        evaluate(exp['func'], env, call_callback)
    else:
        raise Exception("I don'tt know how to evaluate " + exp['type'])


def apply_op(op, a, b):
    def num(x):
        from numbers import Number
        if isinstance(x, Number):
            return x
        else:
            raise Exception(f"Expected number but got {x}")

    def div(x):
        if num(x) == 0:
            raise Exception("Divide by zero")
        return x

    if op == "+":
        return num(a) + num(b)
    elif op == "-":
        return num(a) - num(b)
    elif op == "*":
        return num(a) * num(b)
    elif op == "/":
        return num(a) / div(b)
    elif op == "%":
        return num(a) % div(b)
    elif op == "&&":
        if a is not False:
            return b
        return
    elif op == "||":
        if a is not False:
            return a
        return b
    elif op == "<":
        return num(a) < num(b)
    elif op == ">":
        return num(a) > num(b)
    elif op == "<=":
        return num(a) <= num(b)
    elif op == ">=":
        return num(a) >= num(b)
    elif op == "==":
        return a == b
    elif op == "!=":
        return a != b
    raise Exception(f"Can't apply operator {op}")


def make_lambda(env, exp):
    def lambda_function(callback, *args):
        scope = env.extend()
        names = exp['vars']
        args = args[:len(names)]
        for name, value in zip_longest(names, args, fillvalue=False):
            scope.define(name, value)
        evaluate(exp['body'], scope, callback)

    if exp['name']:
        env = env.extend()
        env.define(exp['name'], lambda_function)
    return lambda_function


if __name__ == '__main__':
    code = """
    print-range = λ(a, b, )             # `λ` is synonym to `lambda`
                if a <= b then {  # `then` here is optional as you can see below
                  print(a);
                  if a + 1 <= b {
                    print(", ");
                    print-range(a + 1, b);
                  } else println("");  # newline
                };
    print-range(1, 10);
    fib = lambda(n) if n < 2 then n else fib(n - 1) + fib(n - 2);
    print(fib(6));
"""
    code = """
    print_range = λ(a, b) if a <= b
    {
        print(a);
    if a + 1 <= b {
    print(", ");
    print_range(a + 1, b);
    } else println("");
    };
    print_range(1, 600);
    """
    # code = """a + 1 <= b"""
    code = """
    # cons = lambda(a, b) lambda(f) f(a, b);
    # car = lambda(cell) cell(lambda(a, b) a);
    # cdr = lambda(cell) cell(lambda(a, b) b);
    # NIL = lambda(f) f(NIL, NIL);
    # foreach = lambda(list, f) if list != NIL {
    #     f(car(list));
    #     foreach(cdr(list), f);
    #     };
    # range = lambda(a, b) if a <= b then cons(a, range(a + 1, b)) else NIL;
    # x = cons(1, cons(2, cons(3, cons(4, cons(5, NIL)))));
    cons = lambda(x, y)
                lambda(a, i, v)
                    if a == "get"
                        then if i == 0 then x else y
                        else if i == 0 then x = v else y = v;
    c = lambda(a, i, v)
        if a == "get"
            then if i == 0 then 1 else 2;
            # else if i == 0 then x = v else y = v;
    # println(c("get", 1));
    car = lambda(cell) cell("get", 0);
    cdr = lambda(cell) cell("get", 1);
    set-car! = lambda(cell, val) cell("set", 0, val);
    set-cdr! = lambda(cell, val) cell("set", 1, val);
    NIL = cons(0, 0); 
    set-car!(NIL, NIL);
    set-cdr!(NIL, NIL);
    # # tests
    x = cons(1, 2);
    println(car(x));
    # println((lambda(cond) if cond then 1 else 0)(true));
    println(cdr(x));
    set-car!(x, 10);
    set-cdr!(x, 20);
    println(car(x));
    println(cdr(x));
    # foreach(range(1, 8), lambda(x) println(x * x));
    # foreach(x, println);
    # println(car(x));
    # println(car(cdr(x)));
    # println(car(cdr(cdr(x))));
    # println(car(cdr(cdr(cdr(x)))));
    # println(car(cdr(cdr(cdr(cdr(x))))));
    """
    code = """
    println(let loop (n = 100)
          if n > 0 then n + loop(n - 1)
                   else 0);

    let (x = 2, y = x + 1, z = x + y)
      println(x + y + z);

    # errors out, the vars are bound to the let body
    # print(x + y + z);

    let (x = 10) {
      let (x = x * 2, y = x * x) {
        println(x);  ## 20
        println(y);  ## 400
      };
      println(x);  ## 10
    };
"""
    code = """
    fib = λ(n) if n < 2 then n else fib(n - 1) + fib(n - 2);
    print("fib(10): ");
    time( λ() println(fib(10)) );
    print("fibJS(10): ");
    time( λ() println(fibJS(10)) );

    println("---");

    # print("fib(20): ");
    # time( λ() println(fib(20)) );
    # print("fibJS(20): ");
    # time( λ() println(fibJS(20)) );

    # println("---");
    # 
    # print("fib(27): ");
    # time( λ() println(fib(27)) );
    # print("fibJS(27): ");
    # time( λ() println(fibJS(27)) );
"""
    code = "sum = lambda(x, y) x + y; print(sum(2, 3));"
    code = "let (x=1, y= x + 1) print(x + y);"
    parser = Parser(TokenStream(InputStream(code)))
    ast = parser()
    global_env = Environment()


    def custom_print(callback, txt):
        print(txt, end='')
        callback(False)


    def custom_println(callback, txt):
        print(txt)
        callback(False)


    global_env.define("print", custom_print)
    global_env.define("println", custom_println)

    # def fibJS(callback, n):
    #     if n < 2:
    #         return callback(n)
    #     else:
    #         fibJS(lambda value1: fibJS(lambda value2: callback(value1 + value2), n - 2), n - 1)
    #
    #
    # def time(callback, fn):
    #     def time_callback(value):
    #         t2 = datetime.now()
    #         print(f"Time: {t2 - t1}ms")
    #         callback(value)
    #
    #     from datetime import datetime
    #     t1 = datetime.now()
    #     fn(time_callback)
    #
    #
    # global_env.define("fibJS", fibJS)
    # global_env.define('time', time)
    evaluate(ast, global_env, lambda result: 1)

    # evaluate(ast, global_env)
