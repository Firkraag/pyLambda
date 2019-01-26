#!/usr/bin/env python
# encoding: utf-8
from unittest import TestCase
from evaluator import evaluate
from environment import Environment
from input_stream import InputStream
from token_stream import TokenStream
from parse import Parser


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
        ast = {"type": "binary", "operator": '+', 'left': {"type": "num", "value": 1},
               "right": {"type": "num", "value": 2}}
        self.assertEqual(evaluate(ast, Environment()), 3.0)
        ast = {"type": "prog", "prog": []}
        self.assertEqual(evaluate(ast, Environment()), False)
        ast = {"type": "prog", "prog": [{"type": "num", "value": 1}]}
        self.assertEqual(evaluate(ast, Environment()), 1.0)
        ast = {"type": "prog", "prog": [{"type": "num", "value": 1}, {"type": "num", "value": 2}]}
        self.assertEqual(evaluate(ast, Environment()), 2.0)
        ast = {"type": "assign", "left": {"type": "num", "value": 1.0}, "right": {"type": "str", "value": "a"}}
        with self.assertRaises(Exception):
            evaluate(ast, Environment())
        ast = {"type": "prog", "prog": [
            {"type": "assign", "left": {"type": "var", "value": "a"}, "right": {"type": "str", "value": "foo"}},
            {"type": "var", "value": "a"}]}
        self.assertEqual(evaluate(ast, Environment()), "foo")
        ast = {"type": "assign", "left": {"type": "var", "value": "a"}, "right": {"type": "str", "value": "foo"}}
        with self.assertRaises(Exception):
            evaluate(ast, Environment(Environment()))
        ast = {"type": "call", "func": {"type": "lambda", "vars": ["a"], "body": {"type": "var", "value": "a"}},
               "args": [{"type": "num", "value": 1}]}
        self.assertEqual(evaluate(ast, Environment()), 1.0)
        ast = {"type": "call", "func": {"type": "lambda", "vars": ["a"], "body": {"type": "var", "value": "a"}},
               "args": [{"type": "num", "value": "abc"}]}
        self.assertEqual(evaluate(ast, Environment()), "abc")
        ast = {"type": "if", "cond": {"type": "str", "value": ""}, "then": {"type": "num", "value": 1}}
        self.assertEqual(evaluate(ast, Environment()), 1.0)
        ast = {"type": "if", "cond": {"type": "bool", "value": False}, "then": {"type": "num", "value": 1},
               "else": {"type": "num", "value": 2}}
        self.assertEqual(evaluate(ast, Environment()), 2.0)
        ast = {"type": "if", "cond": {"type": "bool", "value": False}, "then": {"type": "num", "value": 1}}
        self.assertEqual(evaluate(ast, Environment()), False)
        ast = {"type": "foo", "value": 'foo'}
        with self.assertRaises(Exception):
            evaluate(ast, Environment())
