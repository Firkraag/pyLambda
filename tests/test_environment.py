#!/usr/bin/env python
# encoding: utf-8
from unittest import TestCase
from environment import Environment


class TestEnvironment(TestCase):
    def test_extend(self):
        environment = Environment()
        self.assertIsNone(environment._parent)
        subscope = environment.extend()
        self.assertIs(subscope._parent, environment)

    def test_define_and_get(self):
        global_scope = Environment()
        global_scope.define('a', 1)
        self.assertEqual(global_scope.get('a'), 1)
        subscope = global_scope.extend()
        subscope.define('b', 'foo')
        self.assertEqual(subscope.get('b'), 'foo')
        self.assertEqual(subscope.get('a'), 1)
        with self.assertRaises(Exception):
            subscope.get('c')

    def test_lookup(self):
        global_scope = Environment()
        global_scope.define('a', 1)
        subscope = global_scope.extend()
        subscope.define('b', 'foo')
        self.assertIs(subscope.lookup('a'), global_scope)
        self.assertIs(subscope.lookup('b'), subscope)
        self.assertIsNone(subscope.lookup('c'))

    def test_set(self):
        global_scope = Environment()
        global_scope.define('a', 1)
        subscope = global_scope.extend()
        subscope.define('b', 'foo')
        subscope.set('b', 'ccc')
        self.assertEqual(subscope.get('b'), 'ccc')
        with self.assertRaises(Exception):
            subscope.set('c', 'foo')
        global_scope.set('c', 'foo')
        self.assertEqual(global_scope.get('c'), 'foo')
