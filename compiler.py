#!/usr/bin/env python
# encoding: utf-8

from typing import Dict
import sys
from parse import Parser
from token_stream import TokenStream
from input_stream import InputStream
import json

Ast = Dict
_FALSE = {"type": "bool", "value": False}


def js(ast: Ast):
    type_ = ast['type']
    if type_ == "num":
        return _js_atom(ast)
    if type_ == "str":
        return _js_atom(ast)
    if type_ == "bool":
        return _js_atom(ast)
    if type_ == "binary":
        return _js_binary(ast)
    if type_ == "var":
        return js_var(ast)
    if type_ == "assign":
        return _js_assign(ast)
    if type_ == "let":
        return _js_let(ast)
    if type_ == "lambda":
        return _js_lambda(ast)
    if type_ == "if":
        return _js_if(ast)
    if type_ == "call":
        return _js_call(ast)
    if type_ == "prog":
        return _js_prog(ast)
    raise Exception(f"Dunno how to make_js for {ast}")


def _js_atom(ast: Ast):
    return json.dumps(ast['value'])


def js_var(ast: Ast):
    return _make_var(ast['value'])


def _make_var(name):
    return name


def _js_binary(ast: Ast):
    return f"({js(ast['left'])}{ast['operator']}{js(ast['right'])})"


def _js_assign(ast: Ast):
    return _js_binary(ast)


def _js_lambda(ast: Ast):
    code = "(function "
    if 'name' in ast:
        code += _make_var(ast['name'])
    code += "(" + ', '.join(_make_var(var) for var in ast['vars']) + ") {"
    code += "return " + js(ast['body']) + " })"
    return code


def _js_let(ast: Ast):
    if len(ast['vars']) == 0:
        return js(ast['body'])
    # immediately invoked function expression
    iife = {
        'type': 'call',
        'func': {
            'type': 'lambda',
            'vars': [ast['vars'][0]['name']],
            'body': {
                'type': 'let',
                'vars': ast['vars'][1:],
                'body': ast['body'],
            },
        },
        'args': [ast['vars'][0]['def'] or _FALSE],
    }
    return f'({js(iife)})'


def _js_if(ast: Ast):
    cond_code = js(ast['cond'])
    then_code = js(ast['then'])
    else_code = js(ast['else']) if 'else' in ast else 'false'
    return f'({cond_code} != false ? {then_code} : {else_code})'


def _js_prog(ast: Ast):
    return "(" + ", " .join(js(exp) for exp in ast['prog']) + ")"


def _js_call(ast: Ast):
    func_code = js(ast['func'])
    args_code = ", ".join(js(arg) for arg in ast['args'])
    return f'{func_code}({args_code})'


def main():
    with open(sys.argv[1]) as file:
        code = file.read()
    # code = 'let foo(x = 1, y = 1) foo(x + y)'
    # code = 'lambda foo(x) x'
    parser = Parser(TokenStream(InputStream(code)))
    js_code = js(parser())
    print(js_code)


if __name__ == "__main__":
    main()
