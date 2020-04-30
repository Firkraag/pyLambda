#!/usr/bin/env python
# encoding: utf-8
# pylint: disable=missing-docstring
from unittest import TestCase

from ast import (AssignAst, BinaryAst, CallAst, IfAst, LambdaAst, LetAst,
                 LiteralAst, ProgAst, VarAst, VarDefAst, JsAst)
from cps_transformer import (_cps_atom, _cps_binary, _cps_call, _cps_if,
                             _cps_lambda, _cps_let, _cps_prog, to_cps, _cps_js_raw)
from input_stream import InputStream
from parse import Parser
from token_stream import TokenStream


class CpsTransformerTest(TestCase):
    def test_to_cps(self):
        js_raw_ast = JsAst("aa")
        cps_ast = _cps_js_raw(js_raw_ast, lambda x: x)
        self.assertEqual(cps_ast, js_raw_ast)
        atom_ast = LiteralAst(1.0)
        cps_ast = to_cps(atom_ast, lambda x: x)
        self.assertEqual(atom_ast, cps_ast)
        let_ast = LetAst([], LiteralAst(False))
        cps_ast = to_cps(let_ast, lambda x: x)
        self.assertEqual(cps_ast, LiteralAst(False))
        prog_ast = ProgAst([])
        cps_ast = to_cps(prog_ast, lambda x: x)
        self.assertEqual(cps_ast, LiteralAst(False))
        prog_ast = ProgAst([LiteralAst(1)])
        cps_ast = to_cps(prog_ast, lambda x: x)
        self.assertEqual(cps_ast, LiteralAst(1))
        prog_ast = ProgAst([LiteralAst(1), LiteralAst(2)])
        cps_ast = to_cps(prog_ast, lambda x: x)
        self.assertEqual(cps_ast, ProgAst([LiteralAst(1), LiteralAst(2)]))
        if_ast = IfAst(LiteralAst(1), LiteralAst(2), LiteralAst(3))
        cps_ast: CallAst = to_cps(if_ast, lambda x: x)
        expected_ast = CallAst(
            LambdaAst(
                '',
                cps_ast.func.params,
                IfAst(
                    LiteralAst(1),
                    CallAst(VarAst(cps_ast.func.params[0]), [LiteralAst(2)]),
                    CallAst(VarAst(cps_ast.func.params[0]), [LiteralAst(3)]))),
            [LambdaAst(
                '',
                cps_ast.args[0].params,
                VarAst(cps_ast.args[0].params[0]))])
        self.assertEqual(cps_ast, expected_ast)
        lambda_ast = LambdaAst('', ['x', 'y'], LiteralAst(1))
        cps_ast = to_cps(lambda_ast, lambda x: x)
        expected_ast = LambdaAst(
            '',
            [cps_ast.params[0]] + ['x', 'y'],
            CallAst(
                VarAst(cps_ast.params[0]),
                [LiteralAst(1)]))
        self.assertEqual(cps_ast, expected_ast)
        binary_ast = BinaryAst('+', LiteralAst(1), LiteralAst(2))
        cps_ast = to_cps(binary_ast, lambda x: x)
        self.assertEqual(cps_ast, binary_ast)
        parse = Parser(TokenStream(InputStream("a = foo(10);")))
        cps_ast = to_cps(parse(), lambda x: x)
        expected_ast = CallAst(
            VarAst('foo'),
            [
                LambdaAst(
                    '',
                    [cps_ast.args[0].params[0]],
                    AssignAst(VarAst('a'), VarAst(cps_ast.args[0].params[0]))
                ),
                LiteralAst(10)])
        self.assertEqual(cps_ast, expected_ast)

    def test__cps_let(self):
        # let_ast = LetAst(
        #     [VarDefAst('a', LiteralAst(1)), VarDefAst('b', LiteralAst("a"))],
        #     LiteralAst(False))
        let_ast = LetAst([], LiteralAst(False), )
        cps_ast = _cps_let(let_ast, lambda x: x)
        self.assertEqual(cps_ast, LiteralAst(False))
        let_ast = LetAst([VarDefAst('a', LiteralAst(1))], VarAst('a'))
        cps_ast = _cps_let(let_ast, lambda x: x)
        self.assertEqual(
            cps_ast,
            CallAst(
                LambdaAst(
                    '',
                    [cps_ast.func.params[0], 'a'],
                    CallAst(
                        VarAst(cps_ast.func.params[0]),
                        [VarAst('a')])),
                [
                    LambdaAst(
                        '',
                        [cps_ast.args[0].params[0]],
                        VarAst(cps_ast.args[0].params[0])
                    ),
                    LiteralAst(1)]))

    def test__cps_prog(self):
        prog_ast = ProgAst([])
        cps_ast = _cps_prog(prog_ast, lambda x: x)
        self.assertEqual(cps_ast, LiteralAst(False))
        prog_ast = ProgAst([LiteralAst(1)])
        cps_ast = _cps_prog(prog_ast, lambda x: x)
        self.assertEqual(cps_ast, LiteralAst(1))
        prog_ast = ProgAst([LiteralAst(1), LiteralAst(2)])
        cps_ast = _cps_prog(prog_ast, lambda x: x)
        self.assertEqual(cps_ast, ProgAst([LiteralAst(1), LiteralAst(2), ]))
        prog_ast = ProgAst([LiteralAst(1), LiteralAst(2), LiteralAst(3)])
        cps_ast = _cps_prog(prog_ast, lambda x: x)
        self.assertEqual(
            cps_ast,
            ProgAst([
                LiteralAst(1),
                ProgAst([
                    LiteralAst(2),
                    LiteralAst(3)])]))

    def test__cps_atom(self):
        atom_ast = LiteralAst(1.0)
        cps_ast = _cps_atom(atom_ast, lambda x: x)
        self.assertEqual(atom_ast, cps_ast)
        atom_ast = LiteralAst("abc")
        cps_ast = _cps_atom(atom_ast, lambda x: x)
        self.assertEqual(atom_ast, cps_ast)
        atom_ast = LiteralAst(False)
        cps_ast = _cps_atom(atom_ast, lambda x: x)
        self.assertEqual(atom_ast, cps_ast)
        atom_ast = VarAst('a')
        cps_ast = _cps_atom(atom_ast, lambda x: x)
        self.assertEqual(atom_ast, cps_ast)

    def test__cps_if(self):
        if_ast = IfAst(LiteralAst(1), LiteralAst(2), LiteralAst(3))
        cps_ast = _cps_if(if_ast, lambda x: x)
        expected_ast = CallAst(
            LambdaAst(
                '',
                cps_ast.func.params,
                IfAst(
                    LiteralAst(1),
                    CallAst(VarAst(cps_ast.func.params[0]), [LiteralAst(2)]),
                    CallAst(VarAst(cps_ast.func.params[0]), [LiteralAst(3)]))),
            [LambdaAst(
                '',
                cps_ast.args[0].params,
                VarAst(cps_ast.args[0].params[0]))])
        self.assertEqual(cps_ast, expected_ast)
        if_ast = IfAst(LiteralAst(1), LiteralAst(2), LiteralAst(False), )
        cps_ast = _cps_if(if_ast, lambda x: x)
        expected_ast = CallAst(
            LambdaAst(
                '',
                cps_ast.func.params,
                IfAst(
                    LiteralAst(1),
                    CallAst(VarAst(cps_ast.func.params[0]), [LiteralAst(2)]),
                    CallAst(VarAst(cps_ast.func.params[0]), [LiteralAst(False)]))),
            [LambdaAst(
                '',
                cps_ast.args[0].params,
                VarAst(cps_ast.args[0].params[0]))])
        self.assertEqual(cps_ast, expected_ast)

    def test__cps_lambda(self):
        # lambda (x, y) 1
        lambda_ast = LambdaAst('', ['x', 'y'], LiteralAst(1))
        cps_ast = _cps_lambda(lambda_ast, lambda x: x)
        expected_ast = LambdaAst(
            '',
            [cps_ast.params[0]] + ['x', 'y'],
            CallAst(
                VarAst(cps_ast.params[0]),
                [LiteralAst(1)]))
        self.assertEqual(cps_ast, expected_ast)
        # lambda (x, y) x + y
        lambda_ast = LambdaAst(
            '',
            ['x', 'y'],
            BinaryAst('+', VarAst('x'), VarAst('y')))
        cps_ast = _cps_lambda(lambda_ast, lambda x: x)
        # expected result: lambda (continue, args) continue(body)
        expected_ast = LambdaAst(
            '',
            [cps_ast.params[0]] + ['x', 'y'],
            CallAst(
                VarAst(cps_ast.params[0]),
                [BinaryAst('+', VarAst('x'), VarAst('y'))]))
        self.assertEqual(cps_ast, expected_ast)

    def test__cps_call(self):
        call_ast = CallAst(
            VarAst('foo'),
            [LiteralAst(1), LiteralAst(2)])
        cps_ast = _cps_call(call_ast, lambda x: x)
        expected_ast = CallAst(
            VarAst('foo'),
            [
                LambdaAst(
                    '',
                    [cps_ast.args[0].params[0]],
                    VarAst(cps_ast.args[0].params[0]),
                ),
                LiteralAst(1),
                LiteralAst(2)])
        self.assertEqual(cps_ast, expected_ast)

    # TODO
    def test__gensym(self):
        pass

    def test__cps_binary(self):
        binary_ast = BinaryAst('+', LiteralAst(1), LiteralAst(2))
        cps_ast = _cps_binary(binary_ast, lambda x: x)
        self.assertEqual(cps_ast, binary_ast)
        binary_ast = AssignAst(VarAst('a'), LiteralAst(1))
        cps_ast = _cps_binary(binary_ast, lambda x: x)
        self.assertEqual(cps_ast, binary_ast)

    def test__cps_js_raw(self):
        js_raw_ast = JsAst("aa")
        cps_ast = _cps_js_raw(js_raw_ast, lambda x: x)
        self.assertEqual(cps_ast, js_raw_ast)
