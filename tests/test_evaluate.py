#!/usr/bin/env python
# encoding: utf-8
from unittest import TestCase
from evaluator import evaluate
from environment import Environment


# from input_stream import InputStream
# from token_stream import TokenStream
# from parse import Parser


class TestEvaluate(TestCase):
    def test_evaluate(self):
        ast = {"type": "num", "value": 1}
        environment = Environment()
        self.assertEqual(evaluate(ast, environment), 1.0)
        ast = {"type": "bool", "value": True}
        environment = Environment()
        self.assertEqual(evaluate(ast, environment), True)
        ast = {"type": "bool", "value": False}
        environment = Environment()
        self.assertEqual(evaluate(ast, environment), False)
        ast = {"type": "str", "value": "aaa"}
        self.assertEqual(evaluate(ast, Environment()), "aaa")
        ast = {"type": "binary",
               "operator": '+',
               'left': {"type": "num", "value": 1},
               "right": {"type": "num", "value": 2}}
        self.assertEqual(evaluate(ast, Environment()), 3.0)
        ast = {"type": "prog", "prog": []}
        self.assertEqual(evaluate(ast, Environment()), False)
        ast = {"type": "prog", "prog": [{"type": "num", "value": 1}]}
        self.assertEqual(evaluate(ast, Environment()), 1.0)
        ast = {"type": "prog",
               "prog": [{"type": "num", "value": 1},
                        {"type": "num", "value": 2}]}
        self.assertEqual(evaluate(ast, Environment()), 2.0)
        ast = {"type": "assign",
               "left": {"type": "num", "value": 1.0},
               "right": {"type": "str", "value": "a"}}
        with self.assertRaises(Exception):
            evaluate(ast, Environment())
        ast = {"type": "prog",
               "prog": [{"type": "assign",
                         "left": {"type": "var", "value": "a"},
                         "right": {"type": "str", "value": "foo"}},
                        {"type": "var", "value": "a"}]}
        self.assertEqual(evaluate(ast, Environment()), "foo")
        ast = {"type": "assign",
               "left": {"type": "var", "value": "a"},
               "right": {"type": "str", "value": "foo"}}
        with self.assertRaises(Exception):
            evaluate(ast, Environment(Environment()))
        ast = {"type": "call",
               "func": {"type": "lambda",
                        "name": "",
                        "vars": ["a"],
                        "body": {"type": "var", "value": "a"}},
               "args": [{"type": "num", "value": 1}]}
        self.assertEqual(evaluate(ast, Environment()), 1.0)
        ast = {"type": "call",
               "func": {"type": "lambda",
                        "name": "",
                        "vars": ["a"],
                        "body": {"type": "var", "value": "a"}},
               "args": [{"type": "num", "value": "abc"}]}
        self.assertEqual(evaluate(ast, Environment()), "abc")
        # (λ loop (n) if n > 0 then n + loop(n - 1) else 0) (10)
        ast = {"type": "call",
               "func": {"type": "lambda",
                        "name": "loop",
                        "vars": ["n"],
                        "body": {"type": "if",
                                 "cond": {"type": "binary",
                                          "operator": ">",
                                          "left": {"type": "var",
                                                   "value": "n"},
                                          "right": {"type": "num",
                                                    "value": 0}},
                                 "then": {"type": "binary",
                                          "operator": "+",
                                          "left": {"type": "var",
                                                   "value": "n"},
                                          "right": {
                                            "type": "call",
                                            "func": {"type": "var",
                                                     "value": "loop"},
                                            "args": [{
                                                "type": "binary",
                                                "operator": "-",
                                                "left": {"type": "var",
                                                         "value": "n"},
                                                "right": {"type": "num",
                                                          "value": 1.0}}]}},
                                 "else": {"type": "num", "value": 0}}},
               "args": [{"type": "num", "value": 10}]}
        self.assertEqual(evaluate(ast, Environment()), 55.0)
        # let (x) x;
        ast = {"type": "let",
               "vars": [{"name": "x", "def": None}],
               "body": {"type": "var", "value": "x"}}
        self.assertEqual(evaluate(ast, Environment()), False)
        # let (x = 2, y = x + 1, z = x + y) x + y + z
        ast = {'type': 'let',
               'vars': [{'name': 'x', 'def': {'type': 'num', 'value': 2.0}},
                        {'name': 'y',
                         'def': {'type': 'binary',
                                 'operator': '+',
                                 'left': {'type': 'var', 'value': 'x'},
                                 'right': {'type': 'num', 'value': 1.0}}},
                        {'name': 'z',
                         'def': {'type': 'binary',
                                 'operator': '+',
                                 'left': {'type': 'var', 'value': 'x'},
                                 'right': {'type': 'var', 'value': 'y'}}}],
               'body': {'type': 'binary',
                        'operator': '+',
                        'left': {'type': 'binary',
                                 'operator': '+',
                                 'left': {'type': 'var', 'value': 'x'},
                                 'right': {'type': 'var', 'value': 'y'}},
                        'right': {'type': 'var', 'value': 'z'}}}
        self.assertEqual(evaluate(ast, Environment()), 10.0)
        # the second expression will result an errors,
        # since x, y, z are bound to the let body
        # let (x = 2, y = x + 1, z = x + y) x + y + z; x + y + z
        ast = {"type": "prog",
               "prog": [{'type': 'let',
                         'vars': [{'name': 'x',
                                   'def': {'type': 'num', 'value': 2.0}},
                                  {'name': 'y',
                                   'def': {'type': 'binary',
                                           'operator': '+',
                                           'left': {'type': 'var',
                                                    'value': 'x'},
                                           'right': {'type': 'num',
                                                     'value': 1.0}}},
                                  {'name': 'z',
                                   'def': {'type': 'binary',
                                           'operator': '+',
                                           'left': {'type': 'var',
                                                    'value': 'x'},
                                           'right': {'type': 'var',
                                                     'value': 'y'}}}],
                         'body': {'type': 'binary',
                                  'operator': '+',
                                  'left': {'type': 'binary',
                                           'operator': '+',
                                           'left': {'type': 'var',
                                                    'value': 'x'},
                                           'right': {'type': 'var',
                                                     'value': 'y'}},
                                  'right': {'type': 'var', 'value': 'z'}}},
                        {'type': 'binary',
                            'operator': '+',
                            'left': {'type': 'binary',
                                     'operator': '+',
                                     'left': {'type': 'var', 'value': 'x'},
                                     'right': {'type': 'var', 'value': 'y'}},
                            'right': {'type': 'var', 'value': 'z'}}]}
        with self.assertRaises(Exception):
            evaluate(ast, Environment())
        ast = {"type": "if",
               "cond": {"type": "str", "value": ""},
               "then": {"type": "num", "value": 1}}
        self.assertEqual(evaluate(ast, Environment()), 1.0)
        ast = {"type": "if",
               "cond": {"type": "bool", "value": False},
               "then": {"type": "num", "value": 1},
               "else": {"type": "num", "value": 2}}
        self.assertEqual(evaluate(ast, Environment()), 2.0)
        ast = {"type": "if",
               "cond": {"type": "bool", "value": False},
               "then": {"type": "num", "value": 1}}
        self.assertEqual(evaluate(ast, Environment()), False)
        ast = {"type": "foo", "value": 'foo'}
        with self.assertRaises(Exception):
            evaluate(ast, Environment())
