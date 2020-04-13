#!/usr/bin/env python
# encoding: utf-8
"""
Compile ast to javascript code, write it to stdout,
gaining an dramatic speed improvement compared to interpreting the AST.
"""
import json
import sys
from typing import Union
from ast import Ast, LiteralAst, BinaryAst, VarAst, AssignAst, LetAst,\
    LambdaAst, IfAst, CallAst, ProgAst
from input_stream import InputStream
from parse import Parser
from token_stream import TokenStream

# pylint: disable=C0111


def to_js(ast: Ast) -> str:
    try:
        function = _MAPPING[type(ast)]
    except Exception:
        raise Exception(f"Dunno how to make_js for {ast}")
    else:
        return function(ast)


def _js_atom(ast: LiteralAst) -> str:
    return json.dumps(ast.value)


def _js_var(ast: VarAst) -> str:
    return _make_var(ast.name)


def _make_var(name: str) -> str:
    return name


def _js_binary(ast: Union[AssignAst, BinaryAst]) -> str:
    return f"({to_js(ast.left)} {ast.operator} {to_js(ast.right)})"


def _js_assign(ast: AssignAst) -> str:
    return f"({to_js(ast.left)} = {to_js(ast.right)})"


def _js_lambda(ast: LambdaAst) -> str:
    code = "(function "
    if ast.name:
        code += _make_var(ast.name)
    code += "(" + ', '.join(_make_var(var) for var in ast.params) + ") {"
    code += "return " + to_js(ast.body) + " })"
    return code


def _js_let(ast: LetAst) -> str:
    if not ast.vardefs:
        return to_js(ast.body)
    # immediately invoked function expression
    iife = CallAst(
        LambdaAst(
            '',
            [ast.vardefs[0].name],
            LetAst(
                ast.vardefs[1:],
                ast.body)),
        [ast.vardefs[0].define or LiteralAst(False)])
    return f'({to_js(iife)})'


def _js_if(ast: IfAst) -> str:
    cond_code = to_js(ast.cond)
    then_code = to_js(ast.then)
    else_code = to_js(ast.else_) if ast.else_ else 'false'
    return f'({cond_code} !== false ? {then_code} : {else_code})'


def _js_prog(ast: ProgAst) -> str:
    if ast.prog:
        return "(" + ", ".join(to_js(exp) for exp in ast.prog) + ")"
    return '(false)'


def _js_call(ast: CallAst) -> str:
    func_code = to_js(ast.func)
    args_code = ", ".join(to_js(arg) for arg in ast.args)
    return f'{func_code}({args_code})'


_MAPPING = {
    LiteralAst: _js_atom,
    BinaryAst: _js_binary,
    VarAst: _js_var,
    AssignAst: _js_assign,
    LetAst: _js_let,
    LambdaAst: _js_lambda,
    IfAst: _js_if,
    CallAst: _js_call,
    ProgAst: _js_prog,
}

# pylint: disable=C0111


def main():
    with open(sys.argv[1]) as file:
        code = file.read()
    # code = 'let foo(x = 1, y = 1) foo(x + y)'
    # code = 'lambda foo(x) x'
    parser = Parser(TokenStream(InputStream(code)))
    js_code = to_js(parser())
    print(js_code)


if __name__ == "__main__":
    main()
