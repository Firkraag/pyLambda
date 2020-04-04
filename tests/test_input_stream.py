#!/usr/bin/env python
# encoding: utf-8
from random import choice
from string import printable
from unittest import TestCase

from input_stream import InputStream


class TestInputStream(TestCase):
    def setUp(self):
        pass

    def test_next(self):
        self.assertEqual(InputStream('').next(), '')
        for length in range(10):
            input_ = ''.join([choice(printable) for _ in range(length)])
            input_stream = InputStream(input_)
            for i in range(length):
                self.assertEqual(input_[i], input_stream.next())
            for i in range(length, 2 * length + 1):
                self.assertEqual('', input_stream.next())

    def test_peek(self):
        for length in range(10):
            input_ = ''.join([choice(printable) for _ in range(length)])
            input_stream = InputStream(input_)
            for i in range(length):
                self.assertEqual(input_[i], input_stream.peek())
                input_stream.next()
            for i in range(length, 2 * length + 1):
                self.assertEqual('', input_stream.peek())

    def test_eof(self):
        for length in range(10):
            input_ = ''.join([choice(printable) for _ in range(length)])
            input_stream = InputStream(input_)
            for _ in range(length):
                self.assertFalse(input_stream.eof())
                input_stream.next()
            self.assertTrue(input_stream.eof())
