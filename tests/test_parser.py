#!/usr/bin/env python
# encoding: utf-8
from unittest import TestCase
from parser import Parser
from token_stream import TokenStream
from input_stream import InputStream


class TestParser(TestCase):
    def test_skip_punc(self):
        self.fail()

    def test_is_punc(self):
        self.fail()

    def test_skip_kw(self):
        self.fail()

    def test_is_kw(self):
        self.fail()

    def test_skip_op(self):
        self.fail()

    def test_is_op(self):
        self.fail()

    def test_parse_varname(self):
        parser = Parser(TokenStream(InputStream('foo')))
        self.assertEqual(parser.parse_varname(), 'foo')

        parser = Parser(TokenStream(InputStream('1')))
        with self.assertRaises(Exception):
            parser.parse_varname()

    def test_delimited(self):
        parser = Parser(TokenStream(InputStream('{a, b, c}')))
        self.assertEqual(parser.delimited('{', '}', ',', parser.parse_varname), ['a', 'b', 'c'])
        parser = Parser(TokenStream(InputStream('{}')))
        self.assertEqual(parser.delimited('{', '}', ',', parser.parse_varname), [])
        parser = Parser(TokenStream(InputStream('{a,}')))
        self.assertEqual(parser.delimited('{', '}', ',', parser.parse_varname), ['a'])
        parser = Parser(TokenStream(InputStream('{a,b,}')))
        self.assertEqual(parser.delimited('{', '}', ',', parser.parse_varname), ['a', 'b'])

    def test_parse_lambda(self):
        parser = Parser(TokenStream(InputStream('lambda (a, b) 1')))
        self.assertEqual(parser.parse_lambda('lambda'),
                         {'type': 'lambda', 'name': '', 'vars': ['a', 'b'], 'body': {'type': 'num', 'value': 1.0}})
        parser = Parser(TokenStream(InputStream('lambda foo () "abc"')))
        self.assertEqual(parser.parse_lambda('lambda'),
                         {'type': 'lambda', 'name': 'foo', 'vars': [], 'body': {'type': 'str', 'value': 'abc'}})

    def test_parse_let(self):
        self.fail()

    def test_parse_vardef(self):
        self.fail()

    def test_parse_toplevel(self):
        parser = Parser(TokenStream(InputStream('1;"a";foo')))
        self.assertEqual(parser.parse_toplevel(), {'type': 'prog', 'prog': [{'type': 'num', 'value': 1.0},
                                                                            {'type': 'str', 'value': 'a'},
                                                                            {'type': 'var', 'value': 'foo'}]})
        parser = Parser(TokenStream(InputStream('1;"a";foo;')))
        self.assertEqual(parser.parse_toplevel(), {'type': 'prog', 'prog': [{'type': 'num', 'value': 1.0},
                                                                            {'type': 'str', 'value': 'a'},
                                                                            {'type': 'var', 'value': 'foo'}]})
        parser = Parser(TokenStream(InputStream('')))
        self.assertEqual(parser.parse_toplevel(), {'type': 'prog', 'prog': []})

    def test_parse_prog(self):
        parser = Parser(TokenStream(InputStream('{}')))
        self.assertEqual(parser.parse_prog(), {"type": "bool", "value": False})
        parser = Parser(TokenStream(InputStream('{1;}')))
        self.assertEqual(parser.parse_prog(), {"type": "num", "value": 1.0})
        parser = Parser(TokenStream(InputStream('{1;"bc"}')))
        self.assertEqual(parser.parse_prog(),
                         {"type": "prog", "prog": [{"type": "num", "value": 1.0}, {"type": "str", "value": "bc"}]})

    def test_parse_if(self):
        parser = Parser(TokenStream(InputStream('if 1 then 2 else 3')))
        self.assertEqual(parser.parse_if(), {'type': 'if', 'cond': {'type': 'num', 'value': 1.0},
                                             'then': {'type': 'num', 'value': 2.0},
                                             'else': {'type': 'num', 'value': 3.0},
                                             })

        parser = Parser(TokenStream(InputStream('if 1 {2} else 3')))
        self.assertEqual(parser.parse_if(), {'type': 'if', 'cond': {'type': 'num', 'value': 1.0},
                                             'then': {"type": "num", "value": 2.0},
                                             'else': {'type': 'num', 'value': 3.0},
                                             })

        parser = Parser(TokenStream(InputStream('if 1 then 2')))
        self.assertEqual(parser.parse_if(), {'type': 'if', 'cond': {'type': 'num', 'value': 1.0},
                                             'then': {'type': 'num', 'value': 2.0},
                                             })

    def test_parse_atom(self):
        parser = Parser(TokenStream(InputStream('(1)')))
        self.assertEqual(parser.parse_atom(), {"type": "num", "value": 1.0})
        parser = Parser(TokenStream(InputStream('{1;2}')))
        self.assertEqual(parser.parse_atom(),
                         {"type": "prog", "prog": [{"type": "num", "value": 1.0}, {"type": "num", "value": 2.0}]})
        parser = Parser(TokenStream(InputStream('if 1 then 2 else 3')))
        self.assertEqual(parser.parse_atom(),
                         {"type": "if", "cond": {"type": "num", "value": 1.0}, "then": {"type": "num", "value": 2.0},
                          "else": {"type": "num", "value": 3.0}})
        # parser = Parser(TokenStream(InputStream('let (x = 1) 2')))
        # self.assertEqual(parser.parse_atom(),
        #                 {"type": "let", }
        parser = Parser(TokenStream(InputStream('if 1 then 2 else 3')))
        self.assertEqual(parser.parse_atom(),
                         {"type": "if", "cond": {"type": "num", "value": 1.0}, "then": {"type": "num", "value": 2.0},
                          "else": {"type": "num", "value": 3.0}})
        parser = Parser(TokenStream(InputStream('true')))
        self.assertEqual(parser.parse_atom(), {"type": "bool", "value": True})
        parser = Parser(TokenStream(InputStream('false')))
        self.assertEqual(parser.parse_atom(), {"type": "bool", "value": False})
        parser = Parser(TokenStream(InputStream('lambda (n) 1')))
        self.assertEqual(parser.parse_atom(),
                         {"type": "lambda", "name": "", "vars": ["n"], "body": {"type": "num", "value": 1.0}})
        parser = Parser(TokenStream(InputStream('λ (n) 1')))
        self.assertEqual(parser.parse_atom(),
                         {"type": "lambda", "name": "", "vars": ["n"], "body": {"type": "num", "value": 1.0}})
        parser = Parser(TokenStream(InputStream('123.1')))
        self.assertEqual(parser.parse_atom(), {"type": "num", "value": 123.1})
        parser = Parser(TokenStream(InputStream('a')))
        self.assertEqual(parser.parse_atom(), {"type": "var", "value": 'a'})
        parser = Parser(TokenStream(InputStream('"a"')))
        self.assertEqual(parser.parse_atom(), {"type": "str", "value": "a"})
        parser = Parser(TokenStream(InputStream('')))
        with self.assertRaises(Exception):
            parser.parse_atom()
        parser = Parser(TokenStream(InputStream('\x08')))
        with self.assertRaises(Exception):
            parser.parse_atom()

    def test_parse_bool(self):
        self.fail()

    def test_parse_expression(self):
        parser = Parser(TokenStream(InputStream('1() + "ab"()(1, "ab")')))
        self.assertEqual(parser.parse_expression(), {"type": "call", "func": {
            'type': 'binary',
            'operator': '+',
            'left': {"type": "call", 'func': {"type": "num", "value": 1.0}, "args": []},
            'right': {"type": "call", 'func': {"type": "str", "value": "ab"}, "args": []},
        }, 'args': [{"type": "num", "value": 1.0}, {"type": "str", "value": "ab"}]})
        parser = Parser(TokenStream(InputStream('if 1 then 2()()()')))
        self.assertEqual(parser.parse_expression(), {"type": "call", "func": {
            'type': 'if',
            'cond': {"type": "num", "value": 1.0},
            'then': {"type": "call", "func": {"type": "call", "func": {"type": "num", "value": 2.0}, "args": []},
                     'args': []},
        }, 'args': []})

    def test_parse_call(self):
        parser = Parser(TokenStream(InputStream('(b, c)')))
        func_name = {"type": "var", "value": "a"}
        self.assertEqual(parser.parse_call(func_name), {"type": "call", "func": func_name,
                                                        "args": [{"type": "var", "value": "b"},
                                                                 {"type": "var", "value": "c"}]})

    def test_maybe_call(self):
        parser = Parser(TokenStream(InputStream('a(b, c)')))
        self.assertTrue(parser.maybe_call(parser.parse_varname), {"type": "call", "func": {"type": "var", "value": "a"},
                                                                  "args": [{"type": "var", "value": "b"},
                                                                           {"type": "var", "value": "c"}]})
        parser = Parser(TokenStream(InputStream('a')))
        self.assertTrue(parser.maybe_call(parser.parse_varname), {"type": "var", "value": "a"})

    def test_maybe_binary(self):
        self.fail()

    def test_unexpected(self):
        self.fail()
