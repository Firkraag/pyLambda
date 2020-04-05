#!/usr/bin/env python
# encoding: utf-8
from unittest import TestCase
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
        self.assertEqual(parser._delimited('{',
                                           '}',
                                           ',',
                                           parser._parse_varname),
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
        self.assertEqual(parser._parse_lambda('lambda'),
                         {'type': 'lambda', 'name': '', 'vars': ['a', 'b'],
                          'body': {'type': 'num', 'value': 1.0}})
        parser = Parser(TokenStream(InputStream('lambda foo () "abc"')))
        self.assertEqual(parser._parse_lambda('lambda'),
                         {'type': 'lambda', 'name': 'foo', 'vars': [],
                          'body': {'type': 'str', 'value': 'abc'}})

    def test_parse_let(self):
        parser = Parser(TokenStream(InputStream('let (a = 1, b = 2) 1')))
        self.assertEqual(parser._parse_let(),
                         {"type": "let",
                          "vars": [{"name": "a",
                                    "def": {"type": "num", "value": 1.0}},
                                   {"name": "b",
                                    "def": {"type": "num", "value": 2.0}}],
                          'body': {"type": "num", "value": 1.0}})
        parser = Parser(TokenStream(InputStream('let foo (a = 1, b = 2) foo')))
        self.assertEqual(parser._parse_let(),
                         {"type": "call",
                          "func": {"type": "lambda",
                                   "name": "foo",
                                   "vars": ["a", "b"],
                                   "body": {"type": "var", "value": "foo"}},
                          "args": [{"type": "num", "value": 1.0},
                                   {"type": "num", "value": 2.0}], })
        parser = Parser(TokenStream(InputStream('let foo (a, b = 2) foo')))
        self.assertEqual(parser._parse_let(),
                         {"type": "call",
                          "func": {"type": "lambda",
                                   "name": "foo",
                                   "vars": ["a", "b"],
                                   "body": {"type": "var", "value": "foo"}},
                          "args": [{"type": "bool", "value": False},
                                   {"type": "num", "value": 2.0}], })
        parser = Parser(TokenStream(InputStream('let (a, b = 2) 1')))
        self.assertEqual(parser._parse_let(),
                         {"type": "let", "vars": [{"name": "a", "def": None},
                                                  {"name": "b",
                                                   "def": {"type": "num",
                                                           "value": 2.0}}],
                          'body': {"type": "num", "value": 1.0}})

    def test_parse_vardef(self):
        parser = Parser(TokenStream(InputStream('a = 1')))
        self.assertEqual(parser._parse_vardef(),
                         {"name": "a", "def": {"type": "num", "value": 1.0}})
        parser = Parser(TokenStream(InputStream('a')))
        self.assertEqual(parser._parse_vardef(), {"name": "a", "def": None})

    def test_parse_toplevel(self):
        parser = Parser(TokenStream(InputStream('1;"a";foo')))
        self.assertEqual(parser._parse_toplevel(),
                         {'type': 'prog',
                          'prog': [{'type': 'num', 'value': 1.0},
                                   {'type': 'str', 'value': 'a'},
                                   {'type': 'var', 'value': 'foo'}]})
        parser = Parser(TokenStream(InputStream('1;"a";foo;')))
        self.assertEqual(parser._parse_toplevel(),
                         {'type': 'prog',
                          'prog': [{'type': 'num', 'value': 1.0},
                                   {'type': 'str', 'value': 'a'},
                                   {'type': 'var', 'value': 'foo'}]})
        parser = Parser(TokenStream(InputStream('')))
        self.assertEqual(parser._parse_toplevel(),
                         {'type': 'prog', 'prog': []})
        parser = Parser(TokenStream(InputStream('a 1 2')))
        with self.assertRaises(Exception):
            parser._parse_toplevel()

    def test_call(self):
        parser = Parser(TokenStream(InputStream('1;"a";foo')))
        self.assertEqual(parser(), {'type': 'prog',
                                    'prog': [{'type': 'num', 'value': 1.0},
                                             {'type': 'str', 'value': 'a'},
                                             {'type': 'var', 'value': 'foo'}]})
        parser = Parser(TokenStream(InputStream('1;"a";foo;')))
        self.assertEqual(parser(),
                         {'type': 'prog',
                          'prog': [{'type': 'num', 'value': 1.0},
                                   {'type': 'str', 'value': 'a'},
                                   {'type': 'var', 'value': 'foo'}]})
        parser = Parser(TokenStream(InputStream('')))
        self.assertEqual(parser(), {'type': 'prog', 'prog': []})
        parser = Parser(TokenStream(InputStream('a 1 2')))
        with self.assertRaises(Exception):
            parser()

    def test_parse_prog(self):
        parser = Parser(TokenStream(InputStream('{}')))
        self.assertEqual(parser._parse_prog(), {
                         "type": "bool", "value": False})
        parser = Parser(TokenStream(InputStream('{1;}')))
        self.assertEqual(parser._parse_prog(), {"type": "num", "value": 1.0})
        parser = Parser(TokenStream(InputStream('{1;"bc"}')))
        self.assertEqual(parser._parse_prog(),
                         {"type": "prog",
                          "prog": [{"type": "num", "value": 1.0},
                                   {"type": "str", "value": "bc"}]})

    def test_parse_if(self):
        parser = Parser(TokenStream(InputStream('if 1 then 2 else 3')))
        self.assertEqual(parser._parse_if(),
                         {'type': 'if',
                          'cond': {'type': 'num', 'value': 1.0},
                          'then': {'type': 'num', 'value': 2.0},
                          'else': {'type': 'num', 'value': 3.0}, })

        parser = Parser(TokenStream(InputStream('if 1 {2} else 3')))
        self.assertEqual(parser._parse_if(),
                         {'type': 'if',
                          'cond': {'type': 'num', 'value': 1.0},
                          'then': {"type": "num", "value": 2.0},
                          'else': {'type': 'num', 'value': 3.0}, })

        parser = Parser(TokenStream(InputStream('if 1 then 2')))
        self.assertEqual(parser._parse_if(),
                         {'type': 'if',
                          'cond': {'type': 'num', 'value': 1.0},
                          'then': {'type': 'num', 'value': 2.0}, })

    def test_parse_atom(self):
        parser = Parser(TokenStream(InputStream('(1)')))
        self.assertEqual(parser._parse_atom(), {"type": "num", "value": 1.0})
        parser = Parser(TokenStream(InputStream('{1;2}')))
        self.assertEqual(parser._parse_atom(),
                         {"type": "prog",
                          "prog": [{"type": "num", "value": 1.0},
                                   {"type": "num", "value": 2.0}]})
        parser = Parser(TokenStream(InputStream('if 1 then 2 else 3')))
        self.assertEqual(parser._parse_atom(),
                         {"type": "if",
                          "cond": {"type": "num", "value": 1.0},
                          "then": {"type": "num", "value": 2.0},
                          "else": {"type": "num", "value": 3.0}})
        # parser = Parser(TokenStream(InputStream('let (x = 1) 2')))
        # self.assertEqual(parser.parse_atom(),
        #                 {"type": "let", }
        parser = Parser(TokenStream(InputStream('if 1 then 2 else 3')))
        self.assertEqual(parser._parse_atom(),
                         {"type": "if",
                          "cond": {"type": "num", "value": 1.0},
                          "then": {"type": "num", "value": 2.0},
                          "else": {"type": "num", "value": 3.0}})
        parser = Parser(TokenStream(InputStream('true')))
        self.assertEqual(parser._parse_atom(), {"type": "bool", "value": True})
        parser = Parser(TokenStream(InputStream('false')))
        self.assertEqual(parser._parse_atom(), {
                         "type": "bool", "value": False})
        parser = Parser(TokenStream(InputStream('lambda (n) 1')))
        self.assertEqual(parser._parse_atom(),
                         {"type": "lambda",
                          "name": "", "vars": ["n"],
                          "body": {"type": "num", "value": 1.0}})
        parser = Parser(TokenStream(InputStream('λ (n) 1')))
        self.assertEqual(parser._parse_atom(),
                         {"type": "lambda",
                          "name": "",
                          "vars": ["n"],
                          "body": {"type": "num", "value": 1.0}})
        parser = Parser(TokenStream(InputStream('let (a = 1, b = 2) 1')))
        self.assertEqual(parser._parse_atom(),
                         {"type": "let",
                          "vars": [{"name": "a",
                                    "def": {"type": "num", "value": 1.0}},
                                   {"name": "b",
                                    "def": {"type": "num", "value": 2.0}}],
                          'body': {"type": "num", "value": 1.0}})
        parser = Parser(TokenStream(InputStream('123.1')))
        self.assertEqual(parser._parse_atom(), {"type": "num", "value": 123.1})
        parser = Parser(TokenStream(InputStream('a')))
        self.assertEqual(parser._parse_atom(), {"type": "var", "value": 'a'})
        parser = Parser(TokenStream(InputStream('"a"')))
        self.assertEqual(parser._parse_atom(), {"type": "str", "value": "a"})
        parser = Parser(TokenStream(InputStream('')))
        with self.assertRaises(Exception):
            parser._parse_atom()
        parser = Parser(TokenStream(InputStream('&')))
        with self.assertRaises(Exception):
            parser._parse_atom()

    def test_parse_bool(self):
        parser = Parser(TokenStream(InputStream('true')))
        self.assertEqual(parser._parse_bool(), {"type": "bool", "value": True})
        parser = Parser(TokenStream(InputStream('false')))
        self.assertEqual(parser._parse_bool(), {
                         "type": "bool", "value": False})

    def test_parse_expression(self):
        parser = Parser(TokenStream(InputStream('1() + "ab"()(1, "ab")')))
        self.assertEqual(parser._parse_expression(),
                         {"type": "call",
                          "func": {'type': 'binary',
                                   'operator': '+',
                                   'left': {"type": "call",
                                            'func': {"type": "num",
                                                     "value": 1.0},
                                            "args": []},
                                   'right': {"type": "call",
                                             'func': {"type": "str",
                                                      "value": "ab"},
                                             "args": []}, },
                          'args': [{"type": "num", "value": 1.0},
                                   {"type": "str", "value": "ab"}]})
        parser = Parser(TokenStream(InputStream('if 1 then 2()()()')))
        self.assertEqual(parser._parse_expression(),
                         {"type": "call",
                          "func": {'type': 'if',
                                   'cond': {"type": "num", "value": 1.0},
                                   'then': {"type": "call",
                                            "func": {"type": "call",
                                                     "func": {"type": "num",
                                                              "value": 2.0},
                                                     "args": []},
                                            'args': []},
                                   }, 'args': []})
        parser = Parser(TokenStream(InputStream('1 + ')))
        with self.assertRaises(Exception):
            parser._parse_expression()

    def test_parse_call(self):
        parser = Parser(TokenStream(InputStream('(b, c)')))
        func_name = {"type": "var", "value": "a"}
        self.assertEqual(parser._parse_call(func_name),
                         {"type": "call",
                          "func": func_name,
                          "args": [{"type": "var", "value": "b"},
                                   {"type": "var", "value": "c"}]})

    def test_maybe_call(self):
        parser = Parser(TokenStream(InputStream('a(b, c)')))
        self.assertTrue(parser._maybe_call(parser._parse_varname),
                        {"type": "call",
                         "func": {"type": "var", "value": "a"},
                         "args": [{"type": "var", "value": "b"},
                                  {"type": "var", "value": "c"}]})
        parser = Parser(TokenStream(InputStream('a')))
        self.assertTrue(parser._maybe_call(parser._parse_varname),
                        {"type": "var", "value": "a"})

    def test_maybe_binary(self):
        parser = Parser(TokenStream(InputStream('a + b * c')))
        self.assertEqual(parser._maybe_binary(parser._parse_atom(), 0),
                         {"type": "binary", 'operator': '+',
                          'left': {"type": "var", 'value': 'a'},
                          'right': {"type": "binary", 'operator': '*',
                                    'left': {"type": "var", 'value': 'b'},
                                    'right': {"type": "var", "value": 'c'}}})
        parser = Parser(TokenStream(InputStream('a + b = c')))
        self.assertEqual(parser._maybe_binary(parser._parse_atom(), 0),
                         {"type": "assign", 'operator': '=',
                          'left': {"type": "binary", "operator": '+',
                                   'left': {"type": "var", "value": 'a'},
                                   'right': {"type": "var", 'value': 'b'}},
                          'right': {"type": "var", "value": 'c'}})

    def test_unexpected(self):
        parser = Parser(TokenStream(InputStream('a + b * c')))
        with self.assertRaises(Exception):
            parser.unexpected()
