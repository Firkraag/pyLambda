#!/usr/bin/env python
# encoding: utf-8
from typing import Dict, Callable, List, TypeVar

from token_stream import TokenStream, Token

AST = Dict
T = TypeVar('T')  # Can be anything


class Parser:
    PRECEDENCE = {
        "=": 1,
        "||": 2,
        "&&": 3,
        "<": 7, ">": 7, "<=": 7, ">=": 7, "==": 7, "!=": 7,
        "+": 10, "-": 10,
        "*": 20, "/": 20, "%": 20,
    }

    def __init__(self, token_stream: TokenStream):
        self._token_stream = token_stream

    def _skip_punc(self, char: str) -> None:
        if self._is_punc(char):
            self._token_stream.next()
        else:
            self._token_stream.croak(f'Expecting punctuation: "{char}"')

    def _is_punc(self, char: str) -> bool:
        token = self._token_stream.peek()
        return token == Token('punc', char)

    def _skip_kw(self, char: str) -> None:
        if self._is_kw(char):
            self._token_stream.next()
        else:
            self._token_stream.croak(f'Expecting keyword: "{char}"')

    def _is_kw(self, char: str) -> bool:
        token = self._token_stream.peek()
        return token == Token('kw', char)

    def _skip_op(self, char: str) -> None:
        if self._is_op(char):
            self._token_stream.next()
        else:
            self._token_stream.croak(f'Expecting operator: "{char}"')

    def _is_op(self, char: str) -> bool:
        token = self._token_stream.peek()
        return token == Token('op', char)

    def _delimited(self, start: str, stop: str, separator: str,
                   parser: Callable[[], T]) -> List[T]:
        """
        :param start:
        :param stop:
        :param separator:
        :param parser:
        :return: a list of values returned by parser
        """
        ast_list: List = []
        first = True
        self._skip_punc(start)
        while not self._token_stream.eof():
            if self._is_punc(stop):
                break
            if first:
                first = False
            else:
                self._skip_punc(separator)
            if self._is_punc(stop):
                break
            ast_list.append(parser())
        self._skip_punc(stop)
        return ast_list

    def _parse_lambda(self, keyword: str) -> AST:
        self._skip_kw(keyword)
        return {
            'type': 'lambda',
            'name': self._token_stream.next().value
                    if self._token_stream.peek().type == 'var' else '',
            'vars': self._delimited("(", ")", ",", self._parse_varname),
            'body': self._parse_expression(),
        }

    def _parse_let(self) -> AST:
        """
        When it is a named let, if an arg is not followed by some expression,
        then a false value is assigned to the arg by the parser.
        :return:
        """
        self._skip_kw('let')
        if self._token_stream.peek().type == 'var':
            name = self._token_stream.next().value
            defs = self._delimited('(', ')', ',', self._parse_vardef)
            return {
                'type': 'call',
                'func': {
                    'type': 'lambda',
                    'name': name,
                    'vars': [define['name'] for define in defs],
                    'body': self._parse_expression(),
                },
                'args': list(
                    map(lambda define: define['def'] if define['def'] else
                        {"type": "bool", "value": False}, defs))
            }
        return {
            'type': 'let',
            'vars': self._delimited('(', ')', ',', self._parse_vardef),
            'body': self._parse_expression(),
        }

    def _parse_vardef(self) -> AST:
        """
        Parse expression of the form like 'var [= expression]'
        If var is followed by an expression, the value of key 'def'
        is the ast returned by parse_expression,
        otherwise the value of key 'def' is None.
        :return:
        """
        name = self._parse_varname()
        define = None
        if self._is_op('='):
            self._token_stream.next()
            define = self._parse_expression()
        return {'name': name, 'def': define}

    def _parse_varname(self) -> str:
        """
        :return: varname
        """
        token = self._token_stream.next()
        if token.type == 'var':
            return token.value
        self._token_stream.croak('Expecting variable name')

    def _parse_toplevel(self) -> AST:
        prog = []
        while not self._token_stream.eof():
            prog.append(self._parse_expression())
            if not self._token_stream.eof():
                self._skip_punc(";")
        return {
            'type': 'prog',
            'prog': prog,
        }

    def _parse_if(self) -> AST:
        self._skip_kw("if")
        cond = self._parse_expression()
        if not self._is_punc('{'):
            self._skip_kw('then')
        then = self._parse_expression()
        ret = {
            'type': 'if',
            'cond': cond,
            'then': then,
        }
        # print(self._token_stream.peek())
        if self._is_kw('else'):
            self._skip_kw('else')
            ret['else'] = self._parse_expression()
        return ret

    def _parse_atom(self) -> AST:
        """
        parse_atom does the main dispatching job,
        depending on the current token
        :return:
        """

        def parser() -> AST:
            if self._is_punc('('):
                self._skip_punc('(')
                exp = self._parse_expression()
                self._skip_punc(')')
                return exp
            if self._is_punc('{'):
                return self._parse_prog()
            if self._is_kw('if'):
                return self._parse_if()
            if self._is_kw('let'):
                return self._parse_let()
            if self._is_kw('true') or self._is_kw('false'):
                return self._parse_bool()
            if self._is_kw('lambda'):
                return self._parse_lambda('lambda')
            if self._is_kw('λ'):
                return self._parse_lambda('λ')
            token = self._token_stream.next()
            if token.type in {'var', 'num', 'str'}:
                return token._asdict()
            self.unexpected()

        return self._maybe_call(parser)

    def _parse_prog(self) -> AST:
        """
        If the prog is empty, then it just returns FALSE.
        If it has a single expression, it is returned instead of a "prog" node.
        Otherwise it returns a "prog" node containing the expressions.
        :return:
        """
        prog = self._delimited("{", "}", ";", self._parse_expression)
        if len(prog) == 0:
            return {
                'type': 'bool', 'value': False,
            }
        if len(prog) == 1:
            return prog[0]
        return {'type': 'prog', 'prog': prog}

    def _parse_bool(self) -> AST:
        token = self._token_stream.next()
        assert token.type == 'kw'
        return {
            'type': 'bool',
            'value': token.value == 'true',
        }

    def _parse_expression(self) -> AST:
        """
        expression is a form like
        atom1(args1) op1 atom2(args2) op2 atom3(args3)(args)
        :return:
        """

        def parser() -> AST:
            return self._maybe_binary(self._parse_atom(), 0)

        return self._maybe_call(parser)

    def _parse_call(self, func_name: AST) -> AST:
        """
        func_name is parsed by callee before calling parse_call,
        so parse_call only need to parse func args
        :param func_name:
        :return:
        """
        return {
            'type': 'call',
            'func': func_name,
            'args': self._delimited('(', ')', ',', self._parse_expression)
        }

    def _maybe_call(self, parser: Callable[[], AST]) -> AST:
        """
        This function receive a function that is expected to
        parse the current expression.
        If after that expression it sees a ( punctuation token,
        then it must be a "call" node, which is what parse_call() makes.
        :param parser:
        :return:
        """
        expr = parser()
        return self._parse_call(expr) if self._is_punc("(") else expr

    def _maybe_binary(self, left: AST, my_prec: int) -> AST:
        """
        maybe_binary(left, my_prec) is used to compose
        binary expressions like 1 + 2 * 3.
        if operator is =, then ast type is assign,
        otherwise, ast type is binary
        :param left:
        :param my_prec:
        :return:
        """
        token = self._token_stream.peek()
        if token.type != 'op':
            return left
        his_prec = self.PRECEDENCE[token.value]
        if his_prec > my_prec:
            self._token_stream.next()
            right = self._maybe_binary(self._parse_atom(), his_prec)
            binary = {
                'type': 'assign' if token.value == '=' else 'binary',
                'operator': token.value,
                'left': left,
                'right': right
            }
            return self._maybe_binary(binary, my_prec)
        return left

    def __call__(self):
        return self._parse_toplevel()

    def unexpected(self):
        self._token_stream.croak(
            f'Unexpected token: {self._token_stream.peek()}')
