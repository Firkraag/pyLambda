#!/usr/bin/env python
# encoding: utf-8
from unittest import TestCase
from input_stream import InputStream
from token_stream import TokenStream
import string


class TestTokenStream(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.KEYWORDS = "if then let else lambda λ true false ".split()
        cls.ID_START = string.ascii_letters + 'λ_'
        cls.ID = string.ascii_letters + string.digits + '?!-<>='
        cls.OP = "+-*/%=&|<>!"
        cls.PUNC = ",;({}[]"
        cls.WHITESPACE = " \t\n"
        cls.DIGITS = string.digits

    def test_is_keyword(self):
        for keyword in self.KEYWORDS:
            self.assertTrue(TokenStream.is_keyword(keyword))
        self.assertFalse(TokenStream.is_keyword('aaa'))

    def test_is_digit(self):
        for digit in self.DIGITS:
            self.assertTrue(TokenStream.is_digit(digit))
        self.assertFalse(TokenStream.is_digit('a'))

    def test_is_id_start(self):
        for id_start in self.ID_START:
            self.assertTrue(TokenStream.is_id_start(id_start))
        self.assertFalse(TokenStream.is_digit(';'))

    def test_is_id(self):
        for id in self.ID:
            self.assertTrue(TokenStream.is_id(id))
        self.assertFalse(TokenStream.is_digit(';'))

    def test_is_op_char(self):
        for op in self.OP:
            self.assertTrue(TokenStream.is_op_char(op))
        self.assertFalse(TokenStream.is_op_char(';'))

    def test_is_punc(self):
        for punc in self.PUNC:
            self.assertTrue(TokenStream.is_punc(punc))
        self.assertFalse(TokenStream.is_punc('a'))

    def test_is_whitespace(self):
        for whitespace in self.WHITESPACE:
            self.assertTrue(TokenStream.is_whitespace(whitespace))
        self.assertFalse(TokenStream.is_whitespace('a'))

    def test_read_while(self):
        token_stream = TokenStream(InputStream('ab123='))
        result = token_stream._read_while(lambda ch: ch.isalnum())
        self.assertEqual(result, 'ab123')

    def test_read_number(self):
        token_stream = TokenStream(InputStream('123='))
        result = token_stream._read_number()
        self.assertEqual({'type': 'num', 'value': 123.0}, result)

        token_stream = TokenStream(InputStream('123.3.='))
        result = token_stream._read_number()
        self.assertEqual({'type': 'num', 'value': 123.3}, result)

    def test_read_ident(self):
        token_stream = TokenStream(InputStream('a=1'))
        result = token_stream._read_ident()
        self.assertEqual({'type': 'var', 'value': 'a=1'}, result)

        token_stream = TokenStream(InputStream('a = 1'))
        result = token_stream._read_ident()
        self.assertEqual({'type': 'var', 'value': 'a'}, result)

        token_stream = TokenStream(InputStream('let(a = 1'))
        result = token_stream._read_ident()
        self.assertEqual({'type': 'kw', 'value': 'let'}, result)

    def test_read_string(self):
        token_stream = TokenStream(InputStream('"ab"'))
        result = token_stream._read_string()
        self.assertEqual({'type': 'str', 'value': 'ab'}, result)

        token_stream = TokenStream(InputStream('"ab\\c"'))
        result = token_stream._read_string()
        self.assertEqual({'type': 'str', 'value': 'abc'}, result)

        token_stream = TokenStream(InputStream('"abc'))
        with self.assertRaises(Exception):
            token_stream._read_string()

    def test_skip_comment(self):
        token_stream = TokenStream(InputStream('# abc\ndef'))
        token_stream._skip_comment()
        self.assertEqual(token_stream._input_stream.peek(), 'd')

    def test_read_next(self):
        token_stream = TokenStream(InputStream(' # comment\n123 abc "nba" let a=2  >=;'))
        self.assertEqual(token_stream.next(), {'type': 'num', 'value': 123.0})
        self.assertEqual(token_stream.next(), {'type': 'var', 'value': 'abc'})
        self.assertEqual(token_stream.next(), {'type': 'str', 'value': 'nba'})
        self.assertEqual(token_stream.next(), {'type': 'kw', 'value': 'let'})
        self.assertEqual(token_stream.next(), {'type': 'var', 'value': 'a=2'})
        self.assertEqual(token_stream.next(), {'type': 'op', 'value': '>='})
        self.assertEqual(token_stream.next(), {'type': 'punc', 'value': ';'})
        self.assertEqual(token_stream.next(), {})
        token_stream = TokenStream(InputStream('\x08'))
        with self.assertRaises(Exception):
            token_stream._read_next()

    def test_peek_and_next(self):
        token_stream = TokenStream(InputStream(' # comment\n123 abc let a=2  >=;'))
        self.assertEqual(token_stream.peek(), {'type': 'num', 'value': 123.0})
        self.assertEqual(token_stream.peek(), {'type': 'num', 'value': 123.0})
        self.assertEqual(token_stream.next(), {'type': 'num', 'value': 123.0})

        token_stream = TokenStream(InputStream(' # comment\n123 abc let a=2  >=;'))
        self.assertEqual(token_stream.next(), {'type': 'num', 'value': 123.0})
        self.assertEqual(token_stream.peek(), {'type': 'var', 'value': 'abc'})

    def test_eof(self):
        token_stream = TokenStream(InputStream(' # comment\n'))
        self.assertTrue(token_stream.eof())
