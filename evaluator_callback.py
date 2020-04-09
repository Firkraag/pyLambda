#!/usr/bin/env python
# encoding: utf-8
from itertools import zip_longest
from typing import Callable, Any, cast, List

from ast import Ast, LiteralAst, VarAst, AssignAst, BinaryAst, LambdaAst, \
    IfAst, ProgAst, CallAst, LetAst
from callback_primitive import primitive
from environment import Environment
from input_stream import InputStream
from parse import Parser
from token_stream import TokenStream
from utils import apply_op


def evaluate(
        ast: Ast, env: Environment, callback: Callable[[Any], Any]) -> None:
    if isinstance(ast, LiteralAst):
        callback(ast.value)
    elif isinstance(ast, VarAst):
        callback(env.get(ast.name))
    elif isinstance(ast, AssignAst):
        if not isinstance(ast.left, VarAst):
            raise Exception(f"Cannot assign to {ast.left}")
        left: VarAst = cast(VarAst, ast.left)
        evaluate(ast.right, env, lambda right: callback(
            env.set(left.name, right)))
    elif isinstance(ast, BinaryAst):

        def left_callback(left: Any) -> None:
            def right_callback(right: Any) -> None:
                callback(apply_op(ast.operator, left, right))

            evaluate(ast.right, env, right_callback)

        ast = cast(BinaryAst, ast)
        evaluate(ast.left, env, left_callback)
    elif isinstance(ast, LambdaAst):
        callback(make_lambda(env, ast))
    elif isinstance(ast, IfAst):
        if_ast = cast(IfAst, ast)

        def if_callback(cond: Any) -> None:
            if cond is not False:
                evaluate(if_ast.then, env, callback)
            elif if_ast.else_ is not None:
                evaluate(if_ast.else_, env, callback)
            else:
                callback(False)

        evaluate(if_ast.cond, env, if_callback)
    elif isinstance(ast, LetAst):

        def loop(env: Environment, i: int) -> None:
            if i < len(let_ast.vardefs):
                vardef = let_ast.vardefs[i]
                scope = env.extend()
                if vardef.define:
                    def define_callback(value: Any) -> None:
                        scope.define(vardef.name, value)
                        loop(scope, i + 1)

                    evaluate(vardef.define, env, define_callback)
                else:
                    scope.define(vardef.name, False)
                    loop(scope, i + 1)
            else:
                evaluate(let_ast.body, env, callback)

        let_ast = cast(LetAst, ast)
        loop(env, 0)
    elif isinstance(ast, ProgAst):

        def loop(last: Any, i: int) -> None:
            if i < len(prog_ast.prog):
                evaluate(prog_ast.prog[i], env,
                         lambda value: loop(value, i + 1))
            else:
                callback(last)

        prog_ast = cast(ProgAst, ast)
        loop(False, 0)
    elif isinstance(ast, CallAst):

        def call_callback(func: Callable[..., None]) -> None:
            def loop(i: int) -> None:
                def arg_callback(arg: Any) -> None:
                    args[i + 1] = arg
                    loop(i + 1)

                if i < len(call_ast.args):
                    evaluate(call_ast.args[i], env, arg_callback)
                else:
                    func(*args)

            args: List[Callable, ...] = [callback] * (len(call_ast.args) + 1)
            loop(0)

        call_ast = cast(CallAst, ast)
        evaluate(call_ast.func, env, call_callback)
    else:
        raise Exception(f"I don'tt know how to evaluate {ast}")


def make_lambda(env: Environment, ast: LambdaAst):
    def lambda_function(callback: Callable, *args: Any) -> None:
        assert len(ast.params) >= len(args)
        scope = env.extend()
        for name, value in zip_longest(ast.params, args, fillvalue=False):
            scope.define(name, value)
        evaluate(ast.body, scope, callback)

    if ast.name:
        env = env.extend()
        env.define(ast.name, lambda_function)
    return lambda_function


def main():
    # code = "sum = lambda(x, y) x + y; print(sum(2, 3));"
    code = """
    fib = λ(n) if n < 2 then n else fib(n - 1) + fib(n - 2);
    time( λ() println(fib(12)) );
    """
    # code = "print(1 + 2 * 3)"
    # code = """
    # fib = λ(n) if n < 2 then n else fib(n - 1) + fib(n - 2);
    # println(fib(8));
    # """
    parser = Parser(TokenStream(InputStream(code)))
    global_env = Environment()
    for name, func in primitive.items():
        global_env.define(name, func)
    evaluate(parser(), global_env, lambda result: result)


if __name__ == "__main__":
    main()
