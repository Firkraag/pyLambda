#!/usr/bin/env python
# encoding: utf-8
from ast import (AssignAst, BinaryAst, CallAst, IfAst, LambdaAst, LetAst,
                 LiteralAst, ProgAst, VarAst, VarDefAst)
from unittest import TestCase

from environment import Environment
from evaluator import evaluate


class TestEvaluate(TestCase):
    def test_evaluate(self):
        ast = LiteralAst(1.0)
        environment = Environment()
        self.assertEqual(evaluate(ast, environment), 1.0)
        ast = LiteralAst(True)
        environment = Environment()
        self.assertEqual(evaluate(ast, environment), True)
        ast = LiteralAst(False)
        environment = Environment()
        self.assertEqual(evaluate(ast, environment), False)
        ast = LiteralAst("aaa")
        self.assertEqual(evaluate(ast, Environment()), "aaa")
        ast = BinaryAst(
            '+',
            LiteralAst(1),
            LiteralAst(2))
        self.assertEqual(evaluate(ast, Environment()), 3.0)
        ast = ProgAst([])
        self.assertEqual(evaluate(ast, Environment()), False)
        ast = ProgAst([LiteralAst(1)])
        self.assertEqual(evaluate(ast, Environment()), 1.0)
        ast = ProgAst([LiteralAst(1), LiteralAst(2)])
        self.assertEqual(evaluate(ast, Environment()), 2.0)
        ast = AssignAst(LiteralAst(1), LiteralAst("a"))
        with self.assertRaises(Exception):
            evaluate(ast, Environment())
        ast = ProgAst(
            [AssignAst(VarAst('a'), LiteralAst("foo")), VarAst('a')])
        self.assertEqual(evaluate(ast, Environment()), "foo")
        ast = AssignAst(VarAst("a"), LiteralAst("foo"))
        with self.assertRaises(Exception):
            evaluate(ast, Environment(Environment()))
        ast = CallAst(
            LambdaAst("", ["a"], VarAst("a")),
            [LiteralAst(1)],
        )
        self.assertEqual(evaluate(ast, Environment()), 1.0)
        ast = CallAst(
            LambdaAst("", ["a"], VarAst("a")),
            [LiteralAst("abc")],
        )
        self.assertEqual(evaluate(ast, Environment()), "abc")
        # (λ loop (n) if n > 0 then n + loop(n - 1) else 0) (10)
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
        self.assertEqual(evaluate(ast, Environment()), 55.0)
        # let (x) x;
        ast = LetAst([VarDefAst("x", None)], VarAst("x"))
        self.assertEqual(evaluate(ast, Environment()), False)
        # let (x = 2, y = x + 1, z = x + y) x + y + z
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
        self.assertEqual(evaluate(ast, Environment()), 10.0)
        # the second expression will result an errors,
        # since x, y, z are bound to the let body
        # let (x = 2, y = x + 1, z = x + y) x + y + z; x + y + z
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
            evaluate(ast, Environment())
        ast = IfAst(
            LiteralAst(""),
            LiteralAst(1),
            None,
        )
        self.assertEqual(evaluate(ast, Environment()), 1.0)
        ast = IfAst(
            LiteralAst(False),
            LiteralAst(1),
            LiteralAst(2),
        )
        self.assertEqual(evaluate(ast, Environment()), 2.0)
        ast = IfAst(
            LiteralAst(False),
            LiteralAst(1),
            None
        )
        self.assertEqual(evaluate(ast, Environment()), False)
        ast = {"type": "foo", "value": 'foo'}
        with self.assertRaises(Exception):
            evaluate(ast, Environment())
