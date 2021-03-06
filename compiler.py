#!/usr/bin/env python
# encoding: utf-8
"""
Compile ast to javascript code, write it to stdout,
gaining an dramatic speed improvement compared to interpreting the AST.
"""
import json
import sys
from typing import Union

from ast import Ast, LiteralAst, BinaryAst, VarAst, AssignAst, LetAst, \
    LambdaAst, IfAst, CallAst, ProgAst, JsAst
from input_stream import InputStream
from parse import Parser
from token_stream import TokenStream


# pylint: disable=C0111

def to_js(ast: Ast) -> str:
    js_code = _to_js(ast)
    global_variables = ', '.join(name for name, define in ast.env.vars.items() if define.assigned)
    if global_variables:
        global_variables = "let " + global_variables + ";"
    js_code = '"use strict";' + global_variables + js_code
    return js_code


def _to_js(ast: Ast) -> str:
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
    return f"({_to_js(ast.left)} {ast.operator} {_to_js(ast.right)})"


def _js_assign(ast: AssignAst) -> str:
    return f"({_to_js(ast.left)} = {_to_js(ast.right)})"


def _js_lambda(ast: LambdaAst) -> str:
    code = "(function "
    func_name = ast.name or 'β_CC'
    code += _make_var(func_name)
    code += "(" + ', '.join(_make_var(var) for var in ast.params) + ") {"
    if ast.iife_params:
        code += "let "
        code += ', '.join(ast.iife_params) + ';'
    code += f'GUARD(arguments, {func_name});'
    code += "return " + _to_js(ast.body) + " })"
    return code


def _js_let(ast: LetAst) -> str:
    if not ast.vardefs:
        return _to_js(ast.body)
    # immediately invoked function expression
    iife = CallAst(
        LambdaAst(
            '',
            [ast.vardefs[0].name],
            LetAst(
                ast.vardefs[1:],
                ast.body)),
        [ast.vardefs[0].define or LiteralAst(False)])
    return f'({_to_js(iife)})'


def _js_if(ast: IfAst) -> str:
    cond_code = _to_js(ast.cond)
    then_code = _to_js(ast.then)
    else_code = _to_js(ast.else_)
    if not _is_bool(ast.cond):
        cond_code += ' !== false'
    return f'({cond_code} ? {then_code} : {else_code})'


def _is_bool(ast: Ast) -> bool:
    if isinstance(ast, BinaryAst):
        if ast.operator in "< > <= >= == !=".split():
            return True
        if ast.operator in ("&&", "||"):
            return _is_bool(ast.left) and _is_bool(ast.right)
    return False


def _js_prog(ast: ProgAst) -> str:
    if ast.prog:
        return "(" + ", ".join(_to_js(exp) for exp in ast.prog) + ")"
    return '(false)'


def _js_call(ast: CallAst) -> str:
    func_code = _to_js(ast.func)
    args_code = ", ".join(_to_js(arg) for arg in ast.args)
    return f'{func_code}({args_code})'


def _js_raw(ast: JsAst) -> str:
    return f'({ast.js_code})'


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
    JsAst: _js_raw,
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
