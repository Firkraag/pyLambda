#!/usr/bin/env python
# encoding: utf-8
import string
from input_stream import InputStream


class TokenStream(object):
    KEYWORDS = set("if then let else lambda λ true false ".split())
    ID_START = set(string.ascii_letters + 'λ_')
    ID = set(string.ascii_letters + string.digits + '?!-<>=')
    OP = set("+-*/%=&|<>!")
    PUNC = set(",;(){}[]")
    WHITESPACE = set(" \t\n")

    def __init__(self, input_stream: InputStream):
        self._input_stream = input_stream
        self.current = {}

    def is_keyword(self, word: str) -> bool:
        return word in self.KEYWORDS

    def is_digit(self, ch: str) -> bool:
        return ch.isdigit()

    def is_id_start(self, ch: str) -> bool:
        return ch in self.ID_START

    def is_id(self, ch: str) -> bool:
        return ch in self.ID

    def is_op_char(self, ch: str) -> bool:
        return ch in self.OP

    def is_punc(self, ch: str) -> bool:
        return ch in self.PUNC

    def is_whitespace(self, ch: str) -> bool:
        return ch in self.WHITESPACE

    def read_while(self, predicate) -> str:
        l = []
        while (not self._input_stream.eof()) and predicate(self._input_stream.peek()):
            l.append(self._input_stream.next())
        return ''.join(l)

    def read_number(self) -> dict:
        """
        Integer and float with decimal point are allowed, and scientific notation not allowed.
        :return:
        """

        def predicate(ch: str) -> bool:
            nonlocal has_dot
            if ch == '.':
                if has_dot:
                    return False
                has_dot = True
                return True
            return self.is_digit(ch)

        has_dot = False
        number = self.read_while(predicate)
        return {
            "type": "num",
            "value": float(number),
        }

    def read_ident(self) -> dict:
        id = self.read_while(self.is_id)
        return {
            'type': 'kw' if self.is_keyword(id) else "var",
            'value': id,
        }

    def read_string(self) -> dict:
        escaped = False
        l = []
        self._input_stream.next()
        while not self._input_stream.eof():
            ch = self._input_stream.next()
            if escaped:
                l.append(ch)
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == '"':
                return {
                    'type': 'str',
                    'value': ''.join(l)
                }
            else:
                l.append(ch)
        self._input_stream.croak("Has no enclosing double quote for string")

    def skip_comment(self) -> None:
        def predicate(ch: str) -> bool:
            return ch != '\n'

        self.read_while(predicate)
        self._input_stream.next()

    def read_next(self) -> dict:
        """
        read next token
        :return:
        """
        self.read_while(self.is_whitespace)
        if self._input_stream.eof():
            return {}
        ch = self._input_stream.peek()
        if ch == '#':
            self.skip_comment()
            return self.read_next()
        if ch == '"':
            return self.read_string()
        if self.is_digit(ch):
            return self.read_number()
        if self.is_id_start(ch):
            return self.read_ident()
        if self.is_punc(ch):
            return {
                'type': 'punc',
                'value': self._input_stream.next()
            }
        if self.is_op_char(ch):
            return {
                'type': 'op',
                'value': self.read_while(self.is_op_char)
            }
        self._input_stream.croak(f"Can't handle character: {ch}")

    def peek(self) -> dict:
        if self.current:
            return self.current
        self.current = self.read_next()
        return self.current

    def next(self) -> dict:
        current = self.current
        self.current = {}
        if current:
            return current
        return self.read_next()

    def __iter__(self):
        while True:
            token = self.read_next()
            if token:
                yield token
            else:
                break

    def eof(self) -> bool:
        return self.peek() == {}

    def croak(self, msg):
        self._input_stream.croak(msg)


if __name__ == '__main__':
    print(list(TokenStream(InputStream('x = "2 +'))))
