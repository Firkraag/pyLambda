#!/usr/bin/env python
# encoding: utf-8
from unittest import TestCase
from input_stream import InputStream
from string import printable
from random import choice


class TestInputStream(TestCase):
    def setUp(self):
        pass

    def test_next(self):
        # self.assertEqual(InputStream('').next(), '')
        for length in range(10):
            input = ''.join([choice(printable) for _ in range(length)])
            input_stream = InputStream(input)
            for i in range(length):
                self.assertEqual(input[i], input_stream.next())
            for i in range(length, 2 * length + 1):
                self.assertEqual('', input_stream.next())

    def test_peek(self):
        for length in range(10):
            input = ''.join([choice(printable) for _ in range(length)])
            input_stream = InputStream(input)
            for i in range(length):
                self.assertEqual(input[i], input_stream.peek())
                input_stream.next()
            for i in range(length, 2 * length + 1):
                self.assertEqual('', input_stream.peek())

    def test_eof(self):
        for length in range(10):
            input = ''.join([choice(printable) for _ in range(length)])
            input_stream = InputStream(input)
            for i in range(length):
                self.assertFalse(input_stream.eof())
                input_stream.next()
            self.assertTrue(input_stream.eof())
