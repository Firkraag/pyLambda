#!/usr/bin/env python
# encoding: utf-8
"""
Input Stream
"""


class InputStream:
    """
    Input Stream
    """

    def __init__(self, input_: str):
        self._pos: int = 0
        self._line: int = 1
        self._col: int = 0
        self._input: str = input_

    def next(self) -> str:
        """
        returns the next value and also discards it from the stream.
        If there are no more values in the stream, return empty string.
        :return:
        """

        try:
            char = self._input[self._pos]
        except IndexError:
            char = ""
        self._pos += 1
        if char == "\n":
            self._line += 1
            self._col = 0
        else:
            self._col += 1
        return char

    def peek(self) -> str:
        """
        returns the next value but without removing it from the stream.
        If there are no more values in the stream, return empty string.
        :return:
        """
        try:
            return self._input[self._pos]
        except IndexError:
            return ""

    def eof(self) -> bool:
        """
        returns true if and only if there are no more values in the stream.
        :return:
        """
        return self.peek() == ""

    def croak(self, msg: str) -> None:
        """
        raise exception with error msg and error location
        whenever encountered error.
        :param msg:
        :return:
        """
        raise Exception(f"{msg} ({self._line}:{self._col})")
