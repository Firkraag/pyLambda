#!/usr/bin/env python
# encoding: utf-8
# pylint: disable=C0111
from ast import (AssignAst, BinaryAst, CallAst, IfAst, LambdaAst, LetAst,
                 LiteralAst, ProgAst, VarAst, VarDefAst)
from unittest import TestCase

from callback_primitive import primitive
from environment import Environment
from evaluator_callback import evaluate
from input_stream import InputStream
from parse import Parser
from token_stream import TokenStream


class TestEvaluate(TestCase):
    def test_evaluate(self):
        ast = LiteralAst(1.0)
        environment = Environment()
        evaluate(ast, environment, lambda value: self.assertEqual(value, 1.0))
        ast = LiteralAst(True)
        environment = Environment()
        evaluate(ast, environment, self.assertTrue)
        ast = LiteralAst(False)
        environment = Environment()
        evaluate(ast, environment, self.assertFalse)
        ast = LiteralAst("aaa")
        evaluate(ast, Environment(),
                 lambda value: self.assertEqual(value, "aaa"))
        ast = BinaryAst(
            '+',
            LiteralAst(1),
            LiteralAst(2))
        evaluate(
            ast,
            Environment(),
            lambda value: self.assertEqual(value, 3.0))
        ast = ProgAst([])
        evaluate(ast, Environment(), self.assertFalse)
        ast = ProgAst([LiteralAst(1)])
        evaluate(
            ast,
            Environment(),
            lambda value: self.assertEqual(value, 1.0))
        ast = ProgAst([LiteralAst(1), LiteralAst(2)])
        evaluate(
            ast,
            Environment(),
            lambda value: self.assertEqual(value, 2.0))
        ast = AssignAst(LiteralAst(1), LiteralAst("a"))
        with self.assertRaises(Exception):
            evaluate(ast, Environment(), lambda value: value)
        ast = ProgAst(
            [AssignAst(VarAst('a'), LiteralAst("foo")), VarAst('a')])
        evaluate(
            ast,
            Environment(),
            lambda value: self.assertEqual(value, "foo"))
        ast = AssignAst(VarAst("a"), LiteralAst("foo"))
        with self.assertRaises(Exception):
            evaluate(ast, Environment(Environment()), lambda value: value)
        ast = CallAst(
            LambdaAst("", ["a"], VarAst("a")),
            [LiteralAst(1)],
        )
        evaluate(
            ast,
            Environment(),
            lambda value: self.assertEqual(value, 1.0))
        ast = CallAst(
            LambdaAst("", ["a"], VarAst("a")),
            [LiteralAst("abc")],
        )
        evaluate(
            ast,
            Environment(),
            lambda value: self.assertEqual(value, "abc"))
        # # (λ loop (n) if n > 0 then n + loop(n - 1) else 0) (10)
        ast = CallAst(
            LambdaAst(
                "loop",
                ["n"],
                IfAst(
                    BinaryAst(">", VarAst("n"), LiteralAst(0)),
                    BinaryAst("+",
                              VarAst("n"),
                              CallAst(
                                  VarAst("loop"),
                                  [BinaryAst(
                                      '-',
                                      VarAst('n'),
                                      LiteralAst(1))])),
                    LiteralAst(0), ), ),
            [LiteralAst(10)]
        )
        evaluate(
            ast,
            Environment(),
            lambda value: self.assertEqual(value, 55.0))
        # # let (x) x;
        ast = LetAst([VarDefAst("x", None)], VarAst("x"))
        evaluate(ast, Environment(), self.assertFalse)
        # # let (x = 2, y = x + 1, z = x + y) x + y + z
        ast = LetAst(
            [
                VarDefAst("x", LiteralAst(2)),
                VarDefAst("y", BinaryAst(
                    "+",
                    VarAst("x"),
                    LiteralAst(1))),
                VarDefAst("z", BinaryAst(
                    "+",
                    VarAst("x"),
                    VarAst("y"))),
            ],
            BinaryAst(
                "+",
                BinaryAst("+", VarAst("x"), VarAst("y")),
                VarAst("z"),
            )
        )
        evaluate(
            ast,
            Environment(),
            lambda value: self.assertEqual(value, 10.0))
        # # the second expression will result an errors,
        # since x, y, z are bound to the let body
        # # let (x = 2, y = x + 1, z = x + y) x + y + z; x + y + z
        ast = ProgAst([
            LetAst(
                [
                    VarDefAst('x', LiteralAst(2)),
                    VarDefAst(
                        'y', BinaryAst('+', VarAst('x'), LiteralAst(1))),
                    VarDefAst(
                        'z', BinaryAst('+', VarAst('x'), VarAst('y'))),
                ],
                BinaryAst(
                    '+',
                    BinaryAst('+', VarAst('x'), VarAst('y')),
                    VarAst('z'),
                ),
            ),
            BinaryAst(
                '+',
                BinaryAst('+', VarAst('x'), VarAst('y')),
                VarAst('z'),
            ),
        ])
        with self.assertRaises(Exception):
            evaluate(ast, Environment(), lambda value: value)
        ast = IfAst(LiteralAst(""), LiteralAst(1), None)
        evaluate(
            ast,
            Environment(),
            lambda value: self.assertEqual(value, 1.0))
        ast = IfAst(
            LiteralAst(False),
            LiteralAst(1),
            LiteralAst(2))
        evaluate(
            ast,
            Environment(),
            lambda value: self.assertEqual(value, 2.0))
        ast = IfAst(
            LiteralAst(False),
            LiteralAst(1),
            None,
        )
        evaluate(ast, Environment(), self.assertFalse)
        ast = {"type": "foo", "value": 'foo'}
        with self.assertRaises(Exception):
            evaluate(ast, Environment(), lambda value: value)
        # fib = λ(n) if n < 2 then n else fib(n - 1) + fib(n - 2);
        # fib(6);
        #
        ast = ProgAst([
            AssignAst(
                VarAst('fib'),
                LambdaAst(
                    'n',
                    ['n'],
                    IfAst(
                        BinaryAst('<', VarAst('n'), LiteralAst(2)),
                        VarAst('n'),
                        BinaryAst(
                            '+',
                            CallAst(
                                VarAst('fib'),
                                [
                                    BinaryAst('-', VarAst('n'), LiteralAst(1)),
                                ]
                            ),
                            CallAst(
                                VarAst('fib'),
                                [
                                    BinaryAst('-', VarAst('n'), LiteralAst(2)),
                                ]
                            ),
                        )
                    )
                )
            ),
            CallAst(VarAst('fib'), [LiteralAst(6)]),
        ])
        evaluate(
            ast,
            Environment(),
            lambda value: self.assertEqual(value, 8.0))
        ast = IfAst(
            LiteralAst(False),
            LiteralAst(1),
            None
        )
        evaluate(ast, Environment(), self.assertFalse)
        ast = CallAst(
            LiteralAst(1),
            [],
        )
        with self.assertRaises(Exception):
            evaluate(ast, Environment(), self.assertFalse)
        code = """
        2 + twice(3, 4)
        """
        global_env = Environment()
        for name, func in primitive.items():
            global_env.define(name, func)
        parser = Parser(TokenStream(InputStream(code)))
        evaluate(
            parser(),
            global_env,
            lambda result: result)
