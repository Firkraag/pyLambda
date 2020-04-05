#!/usr/bin/env python
# encoding: utf-8
import string
from input_stream import InputStream
from typing import Dict, Optional, Callable, List
from collections import namedtuple

Token = namedtuple('Token', 'type value')
NullToken = Token('null', 'null')


class TokenStream:
    KEYWORDS = set("if then let else lambda λ true false ".split())
    IDENTIFIER_START = set(string.ascii_letters + 'λ_')
    IDENTIFIER = set(string.ascii_letters + string.digits + 'λ_?!-<>=')
    OPERATOR = set("+-*/%=&|<>!")
    PUNCTUATION = set(",;(){}[]")
    WHITESPACE = set(" \t\n")
    DIGITS = set(string.digits)

    def __init__(self, input_stream: InputStream):
        self._input_stream: InputStream = input_stream
        self.current: Token = NullToken

    @classmethod
    def is_keyword(cls, word: str) -> bool:
        return word in cls.KEYWORDS

    @classmethod
    def is_digit(cls, ch: str) -> bool:
        return ch in cls.DIGITS

    @classmethod
    def is_identifier_start(cls, ch: str) -> bool:
        return ch in cls.IDENTIFIER_START

    @classmethod
    def is_identifier(cls, ch: str) -> bool:
        return ch in cls.IDENTIFIER

    @classmethod
    def is_operator(cls, ch: str) -> bool:
        return ch in cls.OPERATOR

    @classmethod
    def is_punctuation(cls, ch: str) -> bool:
        return ch in cls.PUNCTUATION

    @classmethod
    def is_whitespace(cls, ch: str) -> bool:
        return ch in cls.WHITESPACE

    def _read_while(self, predicate: Callable[[str], bool]) -> str:
        """
        Advance input_stream while applying next character to predidate
        evaluates true
        :param predicate:
        :return: the string read while predidate is true
        """
        buffer: List[str] = []
        while (not self._input_stream.eof()) and\
                predicate(self._input_stream.peek()):
            buffer.append(self._input_stream.next())
        return ''.join(buffer)

    def _read_number(self) -> Token:
        """
        Integer and float with decimal point are allowed,
        and scientific notation not allowed.
        :return:
        """

        def predicate(ch: str) -> bool:
            nonlocal has_dot
            if ch == '.':
                # Only one dot is allowed in a number
                if has_dot:
                    return False
                has_dot = True
                return True
            return self.is_digit(ch)

        has_dot = False
        number = self._read_while(predicate)
        return Token("num", float(number))

    def _read_identifier(self) -> Token:
        id = self._read_while(self.is_identifier)
        return Token(
            # identifier is either language keyword or variable
            'kw' if self.is_keyword(id) else "var",
            id,
        )

    def _read_string(self) -> Token:
        self._input_stream.next()
        escaped = False
        buffer: List[str] = []
        while not self._input_stream.eof():
            ch = self._input_stream.next()
            if escaped:
                buffer.append(ch)
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == '"':
                return Token(
                    'str',
                    ''.join(buffer)
                )
            else:
                buffer.append(ch)
        self._input_stream.croak("Has no enclosing double quote for string")

    def _skip_comment(self) -> None:
        def predicate(ch: str) -> bool:
            return ch != '\n'

        self._read_while(predicate)
        self._input_stream.next()

    def _read_next(self) -> Token:
        """
        read next token
        :return:
        """
        self._read_while(self.is_whitespace)
        if self._input_stream.eof():
            return NullToken
        ch = self._input_stream.peek()
        if ch == '#':
            self._skip_comment()
            return self._read_next()
        if ch == '"':
            return self._read_string()
        if self.is_digit(ch):
            return self._read_number()
        if self.is_identifier_start(ch):
            return self._read_identifier()
        if self.is_punctuation(ch):
            return Token(
                'punc',
                self._input_stream.next()
            )
        if self.is_operator(ch):
            return Token(
                'op',
                self._read_while(self.is_operator)
            )
        self._input_stream.croak(f"Can't handle character: {ch}")

    def peek(self) -> Token:
        """
        peek next token
        """
        if self.current.type == 'null':
            self.current = self._read_next()
        return self.current

    def next(self) -> Token:
        """
        read next token
        """
        current, self.current = self.current, NullToken
        if current.type == 'null':
            return self._read_next()
        return current

    def eof(self) -> bool:
        """
        end of token stream
        """
        return self.peek().type == 'null'

    def croak(self, msg: str):
        """
        raise exception with error msg and error location
        whenever encountered error.
        """
        self._input_stream.croak(msg)
