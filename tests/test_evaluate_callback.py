#!/usr/bin/env python
# encoding: utf-8
from unittest import TestCase
from evaluator_callback import evaluate
from environment import Environment


class TestEvaluate(TestCase):
    def test_evaluate(self):
        ast = {"type": "num", "value": 1}
        environment = Environment()
        evaluate(ast, environment, lambda value: self.assertEqual(value, 1.0))
        ast = {"type": "bool", "value": True}
        environment = Environment()
        evaluate(ast, environment, lambda value: self.assertTrue(value))
        ast = {"type": "bool", "value": False}
        environment = Environment()
        evaluate(ast, environment, lambda value: self.assertFalse(value))
        ast = {"type": "str", "value": "aaa"}
        evaluate(ast, Environment(), lambda value: self.assertEqual(value, "aaa"))
        ast = {"type": "binary", "operator": '+', 'left': {"type": "num", "value": 1},
               "right": {"type": "num", "value": 2}}
        evaluate(ast, Environment(), lambda value: self.assertEqual(value, 3.0))
        ast = {"type": "prog", "prog": []}
        evaluate(ast, Environment(), lambda value: self.assertFalse(value))
        ast = {"type": "prog", "prog": [{"type": "num", "value": 1}]}
        evaluate(ast, Environment(), lambda value: self.assertEqual(value, 1.0))
        ast = {"type": "prog", "prog": [{"type": "num", "value": 1}, {"type": "num", "value": 2}]}
        evaluate(ast, Environment(), lambda value: self.assertEqual(value, 2.0))
        ast = {"type": "assign", "left": {"type": "num", "value": 1.0}, "right": {"type": "str", "value": "a"}}
        with self.assertRaises(Exception):
            evaluate(ast, Environment(), lambda value: value)
        ast = {"type": "prog", "prog": [
            {"type": "assign", "left": {"type": "var", "value": "a"}, "right": {"type": "str", "value": "foo"}},
            {"type": "var", "value": "a"}]}
        evaluate(ast, Environment(), lambda value: self.assertEqual(value, "foo"))
        ast = {"type": "assign", "left": {"type": "var", "value": "a"}, "right": {"type": "str", "value": "foo"}}
        with self.assertRaises(Exception):
            evaluate(ast, Environment(Environment()), lambda value: value)
        ast = {"type": "call",
               "func": {"type": "lambda", "name": "", "vars": ["a"], "body": {"type": "var", "value": "a"}},
               "args": [{"type": "num", "value": 1}]}
        evaluate(ast, Environment(), lambda value: self.assertEqual(value, 1.0))
        ast = {"type": "call",
               "func": {"type": "lambda", "name": "", "vars": ["a"], "body": {"type": "var", "value": "a"}},
               "args": [{"type": "num", "value": "abc"}]}
        evaluate(ast, Environment(), lambda value: self.assertEqual(value, "abc"))
        # # (λ loop (n) if n > 0 then n + loop(n - 1) else 0) (10)
        ast = {"type": "call", "func": {"type": "lambda", "name": "loop", "vars": ["n"],
                                        "body": {"type": "if",
                                                 "cond": {
                                                     "type": "binary",
                                                     "operator": ">",
                                                     "left": {"type": "var", "value": "n"},
                                                     "right": {"type": "num", "value": 0}},
                                                 "then": {
                                                     "type": "binary",
                                                     "operator": "+",
                                                     "left": {"type": "var", "value": "n"},
                                                     "right": {
                                                         "type": "call",
                                                         "func": {"type": "var", "value": "loop"},
                                                         "args": [{
                                                             "type": "binary",
                                                             "operator": "-",
                                                             "left": {"type": "var", "value": "n"},
                                                             "right": {"type": "num", "value": 1.0}}]}},
                                                 "else": {"type": "num", "value": 0}}},
               "args": [{"type": "num", "value": 10}]}
        evaluate(ast, Environment(), lambda value: self.assertEqual(value, 55.0))
        # # let (x) x;
        ast = {"type": "let", "vars": [{"name": "x", "def": None}], "body": {"type": "var", "value": "x"}}
        evaluate(ast, Environment(), lambda value: self.assertFalse(value))
        # # let (x = 2, y = x + 1, z = x + y) x + y + z
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
        evaluate(ast, Environment(), lambda value: self.assertEqual(value, 10.0))
        # # the second expression will result an errors, since x, y, z are bound to the let body
        # # let (x = 2, y = x + 1, z = x + y) x + y + z; x + y + z
        ast = {"type": "prog", "prog": [{'type': 'let',
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
                                                  'right': {'type': 'var', 'value': 'z'}}},
                                        {'type': 'binary',
                                         'operator': '+',
                                         'left': {'type': 'binary',
                                                  'operator': '+',
                                                  'left': {'type': 'var', 'value': 'x'},
                                                  'right': {'type': 'var', 'value': 'y'}},
                                         'right': {'type': 'var', 'value': 'z'}}]}
        with self.assertRaises(Exception):
            evaluate(ast, Environment(), lambda value: value)
        ast = {"type": "if", "cond": {"type": "str", "value": ""}, "then": {"type": "num", "value": 1}}
        evaluate(ast, Environment(), lambda value: self.assertEqual(value, 1.0))
        ast = {"type": "if", "cond": {"type": "bool", "value": False}, "then": {"type": "num", "value": 1},
               "else": {"type": "num", "value": 2}}
        evaluate(ast, Environment(), lambda value: self.assertEqual(value, 2.0))
        ast = {"type": "if", "cond": {"type": "bool", "value": False}, "then": {"type": "num", "value": 1}}
        evaluate(ast, Environment(), lambda value: self.assertFalse(value))
        ast = {"type": "foo", "value": 'foo'}
        with self.assertRaises(Exception):
            evaluate(ast, Environment(), lambda value: value)
