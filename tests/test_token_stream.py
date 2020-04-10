#!/usr/bin/env python
# encoding: utf-8
# pylint: disable=W0212
# pylint: disable=C0111
import string
from unittest import TestCase

from input_stream import InputStream
from token_stream import Token, TokenStream


class TestTokenStream(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.KEYWORDS = "if then let else lambda λ true false ".split()
        cls.ID_START = string.ascii_letters + 'λ_'
        cls.ID = string.ascii_letters + string.digits + 'λ_?!-<>='
        cls.OP = "+-*/%=&|<>!"
        cls.PUNC = ",;({}[]"
        cls.WHITESPACE = " \t\n"
        cls.DIGITS = string.digits

    def test_is_keyword(self):
        for keyword in self.KEYWORDS:
            self.assertTrue(TokenStream.is_keyword(keyword))
        self.assertFalse(TokenStream.is_keyword('aaa'))
        self.assertTrue(TokenStream.is_keyword('λ'))

    def test_is_digit(self):
        for digit in self.DIGITS:
            self.assertTrue(TokenStream.is_digit(digit))
        self.assertFalse(TokenStream.is_digit('a'))

    def test_is_id_start(self):
        for id_start in self.ID_START:
            self.assertTrue(TokenStream.is_identifier_start(id_start))
        self.assertFalse(TokenStream.is_identifier_start(';'))

    def test_is_id(self):
        for id_ in self.ID:
            self.assertTrue(TokenStream.is_identifier(id_))
        self.assertFalse(TokenStream.is_identifier(';'))

    def test_is_op_char(self):
        for operator in self.OP:
            self.assertTrue(TokenStream.is_operator(operator))
        self.assertFalse(TokenStream.is_operator(';'))

    def test_is_punc(self):
        for punc in self.PUNC:
            self.assertTrue(TokenStream.is_punctuation(punc))
        self.assertFalse(TokenStream.is_punctuation('a'))

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
        self.assertEqual(Token('num', 123.0), result)

        token_stream = TokenStream(InputStream('123.3.='))
        result = token_stream._read_number()
        self.assertEqual(Token('num', 123.3), result)

    def test_read_ident(self):
        token_stream = TokenStream(InputStream('a=1'))
        result = token_stream._read_identifier()
        self.assertEqual(Token('var', 'a=1'), result)

        token_stream = TokenStream(InputStream('a = 1'))
        result = token_stream._read_identifier()
        self.assertEqual(Token('var', 'a'), result)

        token_stream = TokenStream(InputStream('let(a = 1'))
        result = token_stream._read_identifier()
        self.assertEqual(Token('kw', 'let'), result)

    def test_read_string(self):
        token_stream = TokenStream(InputStream('"ab"'))
        result = token_stream._read_string()
        self.assertEqual(Token('str', 'ab'), result)

        token_stream = TokenStream(InputStream('"ab\\c"'))
        result = token_stream._read_string()
        self.assertEqual(Token('str', 'abc'), result)

        token_stream = TokenStream(InputStream('"abc'))
        with self.assertRaises(Exception):
            token_stream._read_string()

    def test_skip_comment(self):
        token_stream = TokenStream(InputStream('# abc\ndef'))
        token_stream._skip_comment()
        self.assertEqual(token_stream._input_stream.peek(), 'd')

    def test_read_next(self):
        token_stream = TokenStream(
            InputStream(' # comment\n123 abc "nba" let a=2  >=;'))
        self.assertEqual(token_stream._read_next(), Token('num', 123.0))
        self.assertEqual(token_stream._read_next(), Token('var', 'abc'))
        self.assertEqual(token_stream._read_next(), Token('str', 'nba'))
        self.assertEqual(token_stream._read_next(), Token('kw', 'let'))
        self.assertEqual(token_stream._read_next(), Token('var', 'a=2'))
        self.assertEqual(token_stream._read_next(), Token('op', '>='))
        self.assertEqual(token_stream._read_next(), Token('punc', ';'))
        self.assertEqual(token_stream._read_next(), Token('null', 'null'))
        token_stream = TokenStream(InputStream('\x08'))
        with self.assertRaises(Exception):
            token_stream._read_next()

        token_stream = TokenStream(InputStream('λ (n) 1'))
        self.assertEqual(token_stream._read_next(), Token("kw", 'λ'))

    def test_peek_and_next(self):
        token_stream = TokenStream(
            InputStream(' # comment\n123 abc let a=2  >=;'))
        self.assertEqual(token_stream.peek(), Token('num', 123.0))
        self.assertEqual(token_stream.peek(), Token('num', 123.0))
        self.assertEqual(token_stream.next(), Token('num', 123.0))

        token_stream = TokenStream(
            InputStream(' # comment\n123 abc let a=2  >=;'))
        self.assertEqual(token_stream.next(), Token('num', 123.0))
        self.assertEqual(token_stream.next(), Token('var', 'abc'))
        self.assertEqual(token_stream.next(), Token('kw', 'let'))
        self.assertEqual(token_stream.next(), Token('var', 'a=2'))

        token_stream = TokenStream(InputStream('λ (n) 1'))
        self.assertEqual(token_stream.next(), Token("kw", "λ"))
        self.assertEqual(token_stream.next(), Token("punc", "("))
        self.assertEqual(token_stream.next(), Token("var", "n"))
        self.assertEqual(token_stream.next(), Token("punc", ")"))
        self.assertEqual(token_stream.next(), Token("num", 1.0))

    def test_eof(self):
        token_stream = TokenStream(InputStream(' # comment\n'))
        self.assertTrue(token_stream.eof())

    def test_croak(self):
        token_stream = TokenStream(InputStream(' # comment\n'))
        with self.assertRaises(Exception):
            token_stream.croak('foo')
