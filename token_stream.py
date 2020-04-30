#!/usr/bin/env python
# encoding: utf-8
"""
parse input stream into token stream
"""
import string
from collections import namedtuple
from typing import Callable, List

from input_stream import InputStream

Token = namedtuple('Token', 'type value')
NULL_TOKEN = Token('null', 'null')


class TokenStream:
    """
    token stream
    """
    KEYWORDS = set("if then let else lambda λ true false js".split())
    IDENTIFIER_START = set(string.ascii_letters + 'λ_')
    IDENTIFIER = set(string.ascii_letters + string.digits + 'λ_?!-<>=')
    OPERATOR = set("+-*/%=&|<>!")
    PUNCTUATION = set(",;(){}[]")
    WHITESPACE = set(" \t\n")
    DIGITS = set(string.digits)

    def __init__(self, input_stream: InputStream):
        self._input_stream: InputStream = input_stream
        self.current: Token = NULL_TOKEN

    # pylint: disable=C0111
    @classmethod
    def is_keyword(cls, word: str) -> bool:
        return word in cls.KEYWORDS

    # pylint: disable=C0111
    @classmethod
    def is_digit(cls, char: str) -> bool:
        return char in cls.DIGITS

    # pylint: disable=C0111
    @classmethod
    def is_identifier_start(cls, char: str) -> bool:
        return char in cls.IDENTIFIER_START

    # pylint: disable=C0111
    @classmethod
    def is_identifier(cls, char: str) -> bool:
        return char in cls.IDENTIFIER

    # pylint: disable=C0111
    @classmethod
    def is_operator(cls, char: str) -> bool:
        return char in cls.OPERATOR

    # pylint: disable=C0111
    @classmethod
    def is_punctuation(cls, char: str) -> bool:
        return char in cls.PUNCTUATION

    # pylint: disable=C0111
    @classmethod
    def is_whitespace(cls, char: str) -> bool:
        return char in cls.WHITESPACE

    def _read_while(self, predicate: Callable[[str], bool]) -> str:
        """
        Advance input_stream while applying next character to predidate
        evaluates true
        :param predicate:
        :return: the string read while predidate is true
        """
        buffer: List[str] = []
        while (not self._input_stream.eof()) and \
                predicate(self._input_stream.peek()):
            buffer.append(self._input_stream.next())
        return ''.join(buffer)

    def _read_number(self) -> Token:
        """
        Integer and float with decimal point are allowed,
        and scientific notation not allowed.
        :return:
        """

        def predicate(char: str) -> bool:
            nonlocal has_dot
            if char == '.':
                # Only one dot is allowed in a number
                if has_dot:
                    return False
                has_dot = True
                return True
            return self.is_digit(char)

        has_dot = False
        number = self._read_while(predicate)
        return Token("num", float(number))

    def _read_identifier(self) -> Token:
        id_ = self._read_while(self.is_identifier)
        return Token(
            # identifier is either language keyword or variable
            'kw' if self.is_keyword(id_) else "var",
            id_,
        )

    def _read_string(self) -> Token:
        self._input_stream.next()
        escaped = False
        buffer: List[str] = []
        while not self._input_stream.eof():
            char = self._input_stream.next()
            if escaped:
                buffer.append(char)
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                return Token(
                    'str',
                    ''.join(buffer)
                )
            else:
                buffer.append(char)
        self._input_stream.croak("Has no enclosing double quote for string")

    def _skip_comment(self) -> None:
        def predicate(char: str) -> bool:
            return char != '\n'

        self._read_while(predicate)
        self._input_stream.next()

    def _read_next(self) -> Token:
        """
        read next token
        :return:
        """
        self._read_while(self.is_whitespace)
        if self._input_stream.eof():
            return NULL_TOKEN
        char = self._input_stream.peek()
        if char == '#':
            self._skip_comment()
            return self._read_next()
        if char == '"':
            return self._read_string()
        if self.is_digit(char):
            return self._read_number()
        if self.is_identifier_start(char):
            return self._read_identifier()
        if self.is_punctuation(char):
            return Token(
                'punc',
                self._input_stream.next()
            )
        if self.is_operator(char):
            return Token(
                'op',
                self._read_while(self.is_operator)
            )
        self._input_stream.croak(f"Can't handle character: {char}")

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
        current, self.current = self.current, NULL_TOKEN
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
