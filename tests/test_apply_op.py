#!/usr/bin/env python
# encoding: utf-8
from unittest import TestCase
from utils import apply_op


class TestApplyOp(TestCase):
    def test_apply_op(self):
        with self.assertRaises(Exception):
            apply_op('+', 'aa', 'bb')
        with self.assertRaises(Exception):
            apply_op('/', 1, 0)
        self.assertEqual(apply_op('+', 1, 1), 2.0)
        self.assertEqual(apply_op('-', 1, 1), 0.0)
        self.assertEqual(apply_op('*', 1, 1), 1.0)
        self.assertEqual(apply_op('/', 1, 2), 0.5)
        self.assertEqual(apply_op('%', 3, 2), 1.0)
        self.assertEqual(apply_op('%', 3.5, 2.1), 1.4)
        self.assertEqual(apply_op('&&', 1, 2), 2)
        self.assertEqual(apply_op('&&', False, 2), False)
        self.assertEqual(apply_op('||', 1, 2), 1)
        self.assertEqual(apply_op('||', False, 2), 2)
        self.assertEqual(apply_op('>', 2, 1), True)
        self.assertEqual(apply_op('>', 0, 1), False)
        self.assertEqual(apply_op('>', 1, 1), False)
        self.assertEqual(apply_op('<', 2, 1), False)
        self.assertEqual(apply_op('<', 0, 1), True)
        self.assertEqual(apply_op('<', 1, 1), False)
        self.assertEqual(apply_op('<=', 2, 1), False)
        self.assertEqual(apply_op('<=', 0, 1), True)
        self.assertEqual(apply_op('<=', 1, 1), True)
        self.assertEqual(apply_op('>=', 2, 1), True)
        self.assertEqual(apply_op('>=', 0, 1), False)
        self.assertEqual(apply_op('>=', 1, 1), True)
        self.assertEqual(apply_op('==', 'a', 'a'), True)
        self.assertEqual(apply_op('==', 'a', 'b'), False)
        self.assertEqual(apply_op('!=', 'a', 'a'), False)
        self.assertEqual(apply_op('!=', 'a', 'b'), True)
        with self.assertRaises(Exception):
            apply_op('?', 'a', 'b')
