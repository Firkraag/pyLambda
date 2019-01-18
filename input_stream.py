#!/usr/bin/env python
# encoding: utf-8


class InputStream(object):
    def __init__(self, input: str):
        self._pos = 0
        self._line = 1
        self._col = 0
        self._input = input

    def next(self) -> str:
        """
        returns the next value and also discards it from the stream.
        If there are no more values in the stream, return empty string.
        :return:
        """
        try:
            ch = self._input[self._pos]
        except IndexError:
            ch = ""
        finally:
            self._pos += 1
            if ch == "\n":
                self._line += 1
                self._col = 0
            else:
                self._col += 1
            return ch

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

    def croak(self, msg: str):
        """
        raise exception with error msg and error location whenever encountered error.
        :param msg:
        :return:
        """
        raise Exception(msg + " (" + str(self._line) + ":" + str(self._col) + ")")
