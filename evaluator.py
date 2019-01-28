#!/usr/bin/env python
# encoding: utf-8
from itertools import zip_longest
from environment import Environment
from utils import apply_op


def evaluate(ast: dict, env: Environment):
    """
    For num, str, bool nodes, return their value;
    variable are fetched from the environment;
    For assignment, we need to check if the left side is a "var" token(if not,
    throw an error;we don't support assignment to anything else for now),
    then we use env.set to set the value, note that the value needs to be computed first
    by calling evaluate recursively. And in any environment except global environment,
    the assigned variable must be defined previously in some environment. Currently,
    variables are defined only when an lambda function is called or
    an let node is evaluated. That means we cannot define a new variable inside lambda function body.
    A binary node applies node operator to node left operand and right operand.
    A lambda node will actually result in a Python closure, so it will be callable from Python
    just like an ordinary function.
    For a call node we need to call a function. First we evaluate the func, which should return a normal
    Python function, then we evaluate the args and apply that function.
    Evaluating an "if" node is simple: first evaluate the condition. If it's not False then
    evaluate the "then" branch and return its value. Otherwise, evaluate the "else" branch, if present,
    or return False
    A "prog" is a sequence of expressions. We just evaluate them in order and return the value of the last
    one. For am empty sequence, the return value is initialized to False.
    A named let of a form like 'let foo(var = value) body' is equivalent to '(lambda foo(var) body)(value)'

    :param ast:
    :param env:
    :return:
    """
    type = ast['type']
    if type in {'num', 'str', 'bool'}:
        return ast['value']
    elif type == 'var':
        return env.get(ast['value'])
    elif type == 'assign':
        left = ast['left']
        if left['type'] != 'var':
            raise Exception(f"Cannot assign to {ast['left']}")
        return env.set(left['value'], evaluate(ast['right'], env))
    elif type == 'binary':
        return apply_op(ast['operator'], evaluate(ast['left'], env), evaluate(ast['right'], env))
    elif type == 'lambda':
        return make_lambda(env, ast)
    elif type == 'if':
        cond = evaluate(ast['cond'], env)
        if cond is not False:
            return evaluate(ast['then'], env)
        if 'else' in ast:
            return evaluate(ast['else'], env)
        else:
            return False
    elif type == 'prog':
        result = False
        for a in ast['prog']:
            result = evaluate(a, env)
        return result
    elif type == 'call':
        func = evaluate(ast['func'], env)
        return func(*[evaluate(arg, env) for arg in ast['args']])
    elif type == 'let':
        for var in ast['vars']:
            scope = env.extend()
            # if an arg is not assigned some value, then False is assigned to the arg by the evaluator.
            scope.define(var['name'], evaluate(var['def'], env) if var['def'] else False)
            env = scope
        return evaluate(ast['body'], env)
    else:
        raise Exception(f"I don't know how to evaluate {ast['type']}")


def make_lambda(env: Environment, ast: dict):
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

# if __name__ == '__main__':
#     code = """
#     print-range = λ(a, b, )             # `λ` is synonym to `lambda`
#                 if a <= b then {  # `then` here is optional as you can see below
#                   print(a);
#                   if a + 1 <= b {
#                     print(", ");
#                     print-range(a + 1, b);
#                   } else println("");  # newline
#                 };
#     print-range(1, 10);
#     fib = lambda(n) if n < 2 then n else fib(n - 1) + fib(n - 2);
#     print(fib(6));
# """
#     code = """
#     print_range = λ(a, b) if a <= b
#     {
#         print(a);
#     if a + 1 <= b {
#     print(", ");
#     print_range(a + 1, b);
#     } else println("");
#     };
#     print_range(1, 600);
#     """
#     # code = """a + 1 <= b"""
#     code = """
#     # cons = lambda(a, b) lambda(f) f(a, b);
#     # car = lambda(cell) cell(lambda(a, b) a);
#     # cdr = lambda(cell) cell(lambda(a, b) b);
#     # NIL = lambda(f) f(NIL, NIL);
#     # foreach = lambda(list, f) if list != NIL {
#     #     f(car(list));
#     #     foreach(cdr(list), f);
#     #     };
#     # range = lambda(a, b) if a <= b then cons(a, range(a + 1, b)) else NIL;
#     # x = cons(1, cons(2, cons(3, cons(4, cons(5, NIL)))));
#     cons = lambda(x, y)
#                 lambda(a, i, v)
#                     if a == "get"
#                         then if i == 0 then x else y
#                         else if i == 0 then x = v else y = v;
#     c = lambda(a, i, v)
#         if a == "get"
#             then if i == 0 then 1 else 2;
#             # else if i == 0 then x = v else y = v;
#     # println(c("get", 1));
#     car = lambda(cell) cell("get", 0);
#     cdr = lambda(cell) cell("get", 1);
#     set-car! = lambda(cell, val) cell("set", 0, val);
#     set-cdr! = lambda(cell, val) cell("set", 1, val);
#     NIL = cons(0, 0);
#     set-car!(NIL, NIL);
#     set-cdr!(NIL, NIL);
#     # # tests
#     x = cons(1, 2);
#     println(car(x));
#     # println((lambda(cond) if cond then 1 else 0)(true));
#     println(cdr(x));
#     set-car!(x, 10);
#     set-cdr!(x, 20);
#     println(car(x));
#     println(cdr(x));
#     # foreach(range(1, 8), lambda(x) println(x * x));
#     # foreach(x, println);
#     # println(car(x));
#     # println(car(cdr(x)));
#     # println(car(cdr(cdr(x))));
#     # println(car(cdr(cdr(cdr(x)))));
#     # println(car(cdr(cdr(cdr(cdr(x))))));
#     """
#     code = """
#     println(let loop (n = 100)
#           if n > 0 then n + loop(n - 1)
#                    else 0);
#
#     let (x = 2, y = x + 1, z = x + y)
#       println(x + y + z);
#
#     # errors out, the vars are bound to the let body
#     # print(x + y + z);
#
#     let (x = 10) {
#       let (x = x * 2, y = x * x) {
#         println(x);  ## 20
#         println(y);  ## 400
#       };
#       println(x);  ## 10
#     };
# """
#     code = """
#     fib = λ(n) if n < 2 then n else fib(n - 1) + fib(n - 2);
#     print("fib(10): ");
#     time( λ() println(fib(10)) );
#     print("fibJS(10): ");
#     time( λ() println(fibJS(10)) );
#
#     println("---");
#
#     # print("fib(20): ");
#     # time( λ() println(fib(20)) );
#     # print("fibJS(20): ");
#     # time( λ() println(fibJS(20)) );
#
#     # println("---");
#     #
#     # print("fib(27): ");
#     # time( λ() println(fib(27)) );
#     # print("fibJS(27): ");
#     # time( λ() println(fibJS(27)) );
# """
#     code = "sum = lambda(x, y) x + y; print(sum(2, 3));"
#     code = "let (x=1, y= x + 1) print(x + y);"
#     code = 'x = "12'
#     parser = Parser(TokenStream(InputStream(code)))
#     ast = parser()
#     global_env = Environment()
#
#
#     def custom_print(callback, txt):
#         print(txt, end='')
#         callback(False)
#
#
#     def custom_println(callback, txt):
#         print(txt)
#         callback(False)
#
#
#     global_env.define("print", custom_print)
#     global_env.define("println", custom_println)
#
#     # def fibJS(callback, n):
#     #     if n < 2:
#     #         return callback(n)
#     #     else:
#     #         fibJS(lambda value1: fibJS(lambda value2: callback(value1 + value2), n - 2), n - 1)
#     #
#     #
#     # def time(callback, fn):
#     #     def time_callback(value):
#     #         t2 = datetime.now()
#     #         print(f"Time: {t2 - t1}ms")
#     #         callback(value)
#     #
#     #     from datetime import datetime
#     #     t1 = datetime.now()
#     #     fn(time_callback)
#     #
#     #
#     # global_env.define("fibJS", fibJS)
#     # global_env.define('time', time)
#     evaluate_callback(ast, global_env, lambda result: 1)
#
#     # evaluate(ast, global_env)
