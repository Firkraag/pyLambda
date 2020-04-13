#!/usr/bin/env python
# encoding: utf-8

# pylint: disable=W0212
# pylint: disable=C0111
# pylint: disable=too-many-public-methods

from unittest import TestCase

from ast import ProgAst, LiteralAst, VarAst, BinaryAst, AssignAst, CallAst, \
    IfAst, LambdaAst, LetAst, VarDefAst
from parse import Parser
from token_stream import TokenStream
from input_stream import InputStream


class TestParser(TestCase):
    def test_skip_punc(self):
        parser = Parser(TokenStream(InputStream(';')))
        parser._skip_punc(';')
        self.assertTrue(parser._token_stream.eof())
        parser = Parser(TokenStream(InputStream(';')))
        with self.assertRaises(Exception):
            parser._skip_punc('e')

    def test_is_punc(self):
        parser = Parser(TokenStream(InputStream(';')))
        self.assertTrue(parser._is_punc(';'))

    def test_skip_kw(self):
        parser = Parser(TokenStream(InputStream('else')))
        parser._skip_kw('else')
        self.assertTrue(parser._token_stream.eof())
        parser = Parser(TokenStream(InputStream('else')))
        with self.assertRaises(Exception):
            parser._skip_kw('e')

    def test_is_kw(self):
        parser = Parser(TokenStream(InputStream('if')))
        self.assertTrue(parser._is_kw('if'))

    def test_skip_op(self):
        parser = Parser(TokenStream(InputStream('>')))
        parser._skip_op('>')
        self.assertTrue(parser._token_stream.eof())
        parser = Parser(TokenStream(InputStream('>')))
        with self.assertRaises(Exception):
            parser._skip_op('<')

    def test_is_op(self):
        parser = Parser(TokenStream(InputStream('>')))
        self.assertTrue(parser._is_op('>'))

    def test_parse_varname(self):
        parser = Parser(TokenStream(InputStream('foo')))
        self.assertEqual(parser._parse_varname(), 'foo')

        parser = Parser(TokenStream(InputStream('1')))
        with self.assertRaises(Exception):
            parser._parse_varname()

    def test_delimited(self):
        parser = Parser(TokenStream(InputStream('{a, b, c}')))
        self.assertEqual(
            parser._delimited('{', '}', ',', parser._parse_varname),
            ['a', 'b', 'c'])
        parser = Parser(TokenStream(InputStream('{}')))
        self.assertEqual(parser._delimited('{', '}', ',',
                                           parser._parse_varname), [])
        parser = Parser(TokenStream(InputStream('{a,}')))
        self.assertEqual(parser._delimited('{', '}', ',',
                                           parser._parse_varname), ['a'])
        parser = Parser(TokenStream(InputStream('{a,b,}')))
        self.assertEqual(parser._delimited('{', '}', ',',
                                           parser._parse_varname), ['a', 'b'])

    def test_parse_lambda(self):
        parser = Parser(TokenStream(InputStream('lambda (a, b) 1')))
        self.assertEqual(
            parser._parse_lambda('lambda'),
            LambdaAst('', ['a', 'b'], LiteralAst(1)))
        parser = Parser(TokenStream(InputStream('lambda foo () "abc"')))
        self.assertEqual(
            parser._parse_lambda('lambda'),
            LambdaAst('foo', [], LiteralAst('abc')))

    def test_parse_let(self):
        parser = Parser(TokenStream(InputStream('let (a = 1, b = 2) 1')))
        self.assertEqual(parser._parse_let(),
                         LetAst([VarDefAst("a", LiteralAst(1.0)),
                                 VarDefAst("b", LiteralAst(2.0)), ],
                                LiteralAst(1.0),))
        parser = Parser(TokenStream(InputStream('let foo (a = 1, b = 2) foo')))
        self.assertEqual(parser._parse_let(),
                         CallAst(
                             LambdaAst(
                                 'foo',
                                 ['a', 'b'],
                                 VarAst('foo')),
                             [LiteralAst(1), LiteralAst(2), ]))
        parser = Parser(TokenStream(InputStream('let foo (a, b = 2) foo')))
        self.assertEqual(parser._parse_let(),
                         CallAst(
                             LambdaAst('foo', ['a', 'b'], VarAst('foo'),),
                             [LiteralAst(False), LiteralAst(2), ]))
        parser = Parser(TokenStream(InputStream('let (a, b = 2) 1')))
        self.assertEqual(
            parser._parse_let(),
            LetAst(
                [VarDefAst('a', None), VarDefAst('b', LiteralAst(2))],
                LiteralAst(1),))

    def test_parse_vardef(self):
        parser = Parser(TokenStream(InputStream('a = 1')))
        self.assertEqual(
            parser._parse_vardef(),
            VarDefAst('a', LiteralAst(1.0)))

        parser = Parser(TokenStream(InputStream('a')))
        self.assertEqual(parser._parse_vardef(), VarDefAst('a', None))

    def test_parse_toplevel(self):
        parser = Parser(TokenStream(InputStream('1;"a";foo')))
        self.assertEqual(
            parser._parse_toplevel(),
            ProgAst([
                LiteralAst(1.0),
                LiteralAst("a"),
                VarAst('foo')]))
        parser = Parser(TokenStream(InputStream('1;"a";foo;')))
        self.assertEqual(
            parser._parse_toplevel(),
            ProgAst([
                LiteralAst(1.0),
                LiteralAst("a"),
                VarAst('foo')]))
        parser = Parser(TokenStream(InputStream('')))
        self.assertEqual(parser._parse_toplevel(), ProgAst([]))
        parser = Parser(TokenStream(InputStream('a 1 2')))
        with self.assertRaises(Exception):
            parser._parse_toplevel()

    def test_call(self):
        parser = Parser(TokenStream(InputStream('1;"a";foo')))
        self.assertEqual(
            parser(),
            ProgAst([
                LiteralAst(1.0),
                LiteralAst('a'),
                VarAst('foo')]))
        parser = Parser(TokenStream(InputStream('1;"a";foo;')))
        self.assertEqual(
            parser(),
            ProgAst([
                LiteralAst(1.0),
                LiteralAst('a'),
                VarAst('foo')]))
        parser = Parser(TokenStream(InputStream('')))
        self.assertEqual(parser(), ProgAst([]))
        parser = Parser(TokenStream(InputStream('a 1 2')))
        with self.assertRaises(Exception):
            parser()

    def test_parse_prog(self):
        parser = Parser(TokenStream(InputStream('{}')))
        self.assertEqual(
            parser._parse_prog(),
            ProgAst([]))
        parser = Parser(TokenStream(InputStream('{1;}')))
        self.assertEqual(parser._parse_prog(), ProgAst([LiteralAst(1)]))
        parser = Parser(TokenStream(InputStream('{1;"bc"}')))
        self.assertEqual(parser._parse_prog(), ProgAst([
            LiteralAst(1),
            LiteralAst("bc")]))

    def test_parse_if(self):
        parser = Parser(TokenStream(InputStream('if 1 then 2 else 3')))
        self.assertEqual(
            parser._parse_if(),
            IfAst(
                LiteralAst(1.0),
                LiteralAst(2.0),
                LiteralAst(3.0)))

        parser = Parser(TokenStream(InputStream('if 1 {2} else 3')))
        self.assertEqual(
            parser._parse_if(),
            IfAst(
                LiteralAst(1.0),
                ProgAst([LiteralAst(2.0)]),
                LiteralAst(3.0)))

        parser = Parser(TokenStream(InputStream('if 1 then 2')))
        self.assertEqual(
            parser._parse_if(),
            IfAst(LiteralAst(1.0), LiteralAst(2.0), None))

    def test_parse_atom(self):
        parser = Parser(TokenStream(InputStream('(1)')))
        self.assertEqual(parser._parse_atom(), LiteralAst(1))
        parser = Parser(TokenStream(InputStream('{1;2}')))
        self.assertEqual(parser._parse_atom(), ProgAst(
            [LiteralAst(1), LiteralAst(2), ]))
        parser = Parser(TokenStream(InputStream('if 1 then 2 else 3')))
        self.assertEqual(parser._parse_atom(), IfAst(
            LiteralAst(1.0), LiteralAst(2.0), LiteralAst(3.0),))
        # parser = Parser(TokenStream(InputStream('let (x = 1) 2')))
        # self.assertEqual(parser.parse_atom(),
        #                 {"type": "let", }
        parser = Parser(TokenStream(InputStream('true')))
        self.assertEqual(parser._parse_atom(), LiteralAst(True))
        parser = Parser(TokenStream(InputStream('false')))
        self.assertEqual(parser._parse_atom(),
                         LiteralAst(False))
        parser = Parser(TokenStream(InputStream('lambda (n) 1')))
        self.assertEqual(parser._parse_atom(),
                         LambdaAst('', ['n'], LiteralAst(1),))
        parser = Parser(TokenStream(InputStream('λ (n) 1')))
        self.assertEqual(parser._parse_atom(),
                         LambdaAst('', ['n'], LiteralAst(1),))
        parser = Parser(TokenStream(InputStream('let (a = 1, b = 2) 1')))
        self.assertEqual(
            parser._parse_atom(),
            LetAst(
                [VarDefAst('a', LiteralAst(1)), VarDefAst('b', LiteralAst(2))],
                LiteralAst(1)))
        parser = Parser(TokenStream(InputStream('123.1')))
        self.assertEqual(parser._parse_atom(), LiteralAst(123.1))
        parser = Parser(TokenStream(InputStream('a')))
        self.assertEqual(parser._parse_atom(), VarAst('a'))
        parser = Parser(TokenStream(InputStream('"a"')))
        self.assertEqual(parser._parse_atom(), LiteralAst("a"))
        parser = Parser(TokenStream(InputStream('')))
        with self.assertRaises(Exception):
            parser._parse_atom()
        parser = Parser(TokenStream(InputStream('&')))
        with self.assertRaises(Exception):
            parser._parse_atom()

    def test_parse_bool(self):
        parser = Parser(TokenStream(InputStream('true')))
        self.assertEqual(parser._parse_bool(), LiteralAst(True))
        parser = Parser(TokenStream(InputStream('false')))
        self.assertEqual(parser._parse_bool(), LiteralAst(False))

    def test_parse_expression(self):
        parser = Parser(TokenStream(InputStream('1() + "ab"()(1, "ab")')))
        self.assertEqual(
            parser._parse_expression(),
            CallAst(
                BinaryAst('+', CallAst(LiteralAst(1), []),
                          CallAst(LiteralAst('ab'), []),),
                [LiteralAst(1), LiteralAst('ab')]))
        parser = Parser(TokenStream(InputStream('if 1 then 2()()()')))
        self.assertEqual(
            parser._parse_expression(),
            CallAst(
                IfAst(
                    LiteralAst(1),
                    CallAst(CallAst(LiteralAst(2), []), []),
                    None),
                []))

        parser = Parser(TokenStream(InputStream('1 + ')))
        with self.assertRaises(Exception):
            parser._parse_expression()

    def test_parse_call(self):
        parser = Parser(TokenStream(InputStream('(b, c)')))
        func = VarAst('a')
        self.assertEqual(parser._parse_call(func), CallAst(
            func, [VarAst('b'), VarAst('c'), ]))

    def test_maybe_call(self):
        parser = Parser(TokenStream(InputStream('a(b, c)')))
        self.assertTrue(parser._maybe_call(parser._parse_atom),
                        CallAst(VarAst('a'), [VarAst('b'), VarAst('c'), ]))
        parser = Parser(TokenStream(InputStream('a')))
        self.assertTrue(parser._maybe_call(parser._parse_atom),
                        VarAst('a'))

    def test_maybe_binary(self):
        parser = Parser(TokenStream(InputStream('a + b * c')))
        self.assertEqual(
            parser._maybe_binary(parser._parse_atom(), 0),
            BinaryAst(
                '+',
                VarAst('a'),
                BinaryAst('*', VarAst('b'), VarAst('c'))))
        parser = Parser(TokenStream(InputStream('a + b = c')))
        self.assertEqual(
            parser._maybe_binary(parser._parse_atom(), 0),
            AssignAst(
                BinaryAst('+', VarAst('a'), VarAst('b')),
                VarAst('c')))
        parser = Parser(TokenStream(InputStream('a + b + c')))
        self.assertEqual(
            parser._maybe_binary(parser._parse_atom(), 0),
            BinaryAst(
                '+',
                BinaryAst('+', VarAst('a'), VarAst('b')),
                VarAst('c')))

    def test_unexpected(self):
        parser = Parser(TokenStream(InputStream('a + b * c')))
        with self.assertRaises(Exception):
            parser.unexpected()
