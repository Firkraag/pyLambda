"""
Takes an Ast as input and output a equivalent Ast as output,
with the difference that will be in continuation-passing style,
thus solving the problem of stack overflow when we execute js code
compiled from lambda.
"""
import sys
from ast import (AssignAst, Ast, BinaryAst, CallAst, IfAst, LambdaAst, LetAst,
                 LiteralAst, ProgAst, VarAst)
from typing import Callable, Dict, List, Union

from input_stream import InputStream
from parse import Parser
from token_stream import TokenStream
from utils import gensym


# pylint: disable=missing-docstring


def to_cps(ast: Ast, k: Callable[[Ast], Ast]) -> Ast:
    try:
        function = _MAPPING[type(ast)]
    except Exception:
        raise Exception(f"Dunno how to CPS {ast}")
    else:
        return function(ast, k)


def _cps_let(let_ast: LetAst, k: Callable[[Ast], Ast]) -> Ast:
    if not let_ast.vardefs:
        return to_cps(let_ast.body, k)
    return to_cps(
        CallAst(
            LambdaAst(
                '',
                [let_ast.vardefs[0].name],
                LetAst(let_ast.vardefs[1:], let_ast.body)),
            [let_ast.vardefs[0].define if let_ast.vardefs[0].define else LiteralAst(
                False)]),
        k)


def _cps_prog(ast: Ast, k: Callable[[Ast], Ast]) -> Ast:
    def cps_body(body: List[Ast]) -> Ast:
        if not body:
            return k(LiteralAst(False))
        if len(body) == 1:
            return to_cps(body[0], k)
        return to_cps(
            body[0],
            lambda first: ProgAst([first, cps_body(body[1:])]))
    return cps_body(ast.prog)


def _cps_atom(ast: Union[LiteralAst, VarAst], k: Callable[[Ast], Ast]) -> Ast:
    return k(ast)


def _cps_if(if_ast: IfAst, k: Callable[[Ast], Ast]) -> CallAst:
    """
    The previous version of cps_if passed the k on compiling both branches,
    resulting in massive code growth for consecutive if-s.
    The (quite expensive) fix is to wrap the rest of the program
    in a continuation, and we'll transform the "if" node into an IIFE
    which receives that continuation as an argument.
    The body of this IIFE will just call the continuation
    with the result of the if expression.

    The following is a sample transformation:

    a = if foo then 1 else 2;
    print(a);

    (λ (ifcont){
        if foo then ifcont(1) else ifcont(2);
    })(λ (ifret){
        a = ifret;
        print(a);
    });
    """

    def cps_cond(cond_ast: Ast) -> Ast:
        def cps_then_and_else(result: Ast) -> Ast:
            return CallAst(VarAst(if_continuation), [result])

        return IfAst(
            cond_ast,
            to_cps(if_ast.then, cps_then_and_else),
            to_cps(if_ast.else_, cps_then_and_else))

    if_continuation = gensym("I")
    return CallAst(
        LambdaAst('', [if_continuation], to_cps(if_ast.cond, cps_cond)),
        [_make_continuation(k)])


def _cps_lambda(lambda_ast: LambdaAst, k: Callable[[Ast], Ast]) -> Ast:
    continuation = gensym("K")
    body = to_cps(
        lambda_ast.body,
        lambda body: CallAst(VarAst(continuation), [body]))
    return k(LambdaAst(lambda_ast.name, [continuation] + lambda_ast.params, body))


def _cps_call(call_ast: CallAst, k: Callable[[Ast], Ast]) -> Ast:
    def func_callback(func: Ast) -> Ast:
        def loop(args: List[Ast], i: int) -> Ast:
            def arg_callback(arg: Ast) -> Ast:
                args.append(arg)
                return loop(args, i + 1)

            if i == len(call_ast.args):
                return CallAst(func, args)
            return to_cps(call_ast.args[i], arg_callback)

        return loop([_make_continuation(k)], 0)

    return to_cps(call_ast.func, func_callback)


def _make_continuation(k: Callable[[Ast], Ast]) -> LambdaAst:
    continuation = gensym("R")
    return LambdaAst(
        '',
        [continuation],
        k(VarAst(continuation)))


def _cps_binary(ast: Union[AssignAst, BinaryAst], k: Callable[[Ast], Ast]) -> Ast:
    def cps_left(left_ast: Ast) -> Ast:
        def cps_right(right_ast: Ast) -> Ast:
            if isinstance(ast, BinaryAst):
                result_ast = BinaryAst(ast.operator, left_ast, right_ast)
            else:
                result_ast = AssignAst(left_ast, right_ast)
            return k(result_ast)

        return to_cps(ast.right, cps_right)

    return to_cps(ast.left, cps_left)


_MAPPING: Dict[Ast, Callable] = {
    LiteralAst: _cps_atom,
    VarAst: _cps_atom,
    AssignAst: _cps_binary,
    BinaryAst: _cps_binary,
    LetAst: _cps_let,
    LambdaAst: _cps_lambda,
    ProgAst: _cps_prog,
    CallAst: _cps_call,
    IfAst: _cps_if,
}


def main():
    with open(sys.argv[1]) as file:
        code = file.read()
    parser = Parser(TokenStream(InputStream(code)))
    cps_code = to_cps(parser(), lambda ast: CallAst(
        VarAst('β_TOPLEVEL'),
        [ast],
    ))
    print(cps_code)
    # print(to_js(cps_code))


if __name__ == "__main__":
    main()
