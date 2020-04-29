#!/usr/bin/env python
# encoding: utf-8
import sys

from ast import CallAst, VarAst
from compiler import to_js
from cps_transformer import to_cps
from input_stream import InputStream
from optimize import Optimizer
from parse import Parser
from token_stream import TokenStream

with open(sys.argv[1]) as file:
    code = file.read()
parser = Parser(TokenStream(InputStream(code)))
ast = parser()
ast = to_cps(ast, lambda ast: CallAst(
    VarAst('β_TOPLEVEL'),
    [ast],
))
# print(ast)
ast = Optimizer().optimize(ast)
# print(ast)
js_code = to_js(ast)
print(js_code)
