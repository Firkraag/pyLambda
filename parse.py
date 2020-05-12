#!/usr/bin/env python
# encoding: utf-8
"""
parse token_stream into ast
"""
import sys
from typing import Callable, List, TypeVar, Union, cast

from ast import Ast, LiteralAst, VarAst, VarDefAst, LambdaAst, LetAst, \
    CallAst, ProgAst, IfAst, BinaryAst, AssignAst, JsAst
from input_stream import InputStream
from token_stream import TokenStream, Token
from utils import gensym

T = TypeVar('T')  # Can be anything


class Parser:
    """
    parse token stream into ast
    """
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

    def _parse_lambda(self, keyword: str) -> LambdaAst:
        self._skip_kw(keyword)
        if self._token_stream.peek().type == 'var':
            name = self._token_stream.next().value
        else:
            name = ''
        params = self._delimited("(", ")", ",", self._parse_varname)
        body = self._parse_expression()
        return LambdaAst(name, params, body)

    def _parse_let(self) -> Union[CallAst, LetAst]:
        """
        When it is a named let, if an arg is not followed by some expression,
        then a false value is assigned to the arg by the parser.
        :return:
        """
        self._skip_kw('let')
        if self._token_stream.peek().type == 'var':
            name = self._token_stream.next().value
            vardefs = self._delimited('(', ')', ',', self._parse_vardef)
            varnames = [vardef.name for vardef in vardefs]
            defines = [vardef.define if vardef.define else LiteralAst(False)
                       for vardef in vardefs]
            return CallAst(
                LambdaAst(
                    name,
                    varnames,
                    self._parse_expression()),
                defines)
        vardefs = self._delimited('(', ')', ',', self._parse_vardef)
        body = self._parse_expression()
        return LetAst(vardefs, body)

    def _parse_vardef(self) -> VarDefAst:
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
        return VarDefAst(name, define)

    def _parse_varname(self) -> str:
        """
        :return: varname
        """
        token = self._token_stream.next()
        if token.type == 'var':
            return token.value
        return self._token_stream.croak('Expecting variable name')

    def _parse_toplevel(self) -> ProgAst:
        prog = []
        while not self._token_stream.eof():
            prog.append(self._parse_expression())
            if not self._token_stream.eof():
                self._skip_punc(";")
        return ProgAst(prog)

    def _parse_if(self) -> IfAst:
        self._skip_kw("if")
        cond = self._parse_expression()
        if not self._is_punc('{'):
            self._skip_kw('then')
        then = self._parse_expression()
        else_ = LiteralAst(False)
        if self._is_kw('else'):
            self._skip_kw('else')
            else_ = self._parse_expression()
        return IfAst(cond, then, else_)

    def _parse_atom(self) -> Ast:
        """
        parse_atom does the main dispatching job,
        depending on the current token
        :return:
        """

        def parser() -> Ast:
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
            if self._is_kw('js'):
                return self._parse_js_raw()
            token = self._token_stream.next()
            if token.type in ('str', 'num'):
                return LiteralAst(token.value)
            if token.type == 'var':
                return VarAst(token.value)
            self.unexpected()

        return self._maybe_call(parser)

    def _parse_js_raw(self):
        self._token_stream.next()
        token = self._token_stream.next()
        assert token.type == 'str'
        return JsAst(token.value)

    def _parse_prog(self) -> ProgAst:
        """
        If the prog is empty, then it just returns FALSE.
        If it has a single expression, it is returned instead of a "prog" node.
        Otherwise it returns a "prog" node containing the expressions.
        :return:
        """
        prog = self._delimited("{", "}", ";", self._parse_expression)
        # if len(prog) == 0:
        #     return LiteralAst(False)
        # if len(prog) == 1:
        #     return prog[0]
        return ProgAst(prog)

    def _parse_bool(self) -> LiteralAst:
        token = self._token_stream.next()
        assert token.type == 'kw'
        return LiteralAst(token.value == 'true')

    def _parse_expression(self) -> Ast:
        """
        expression is a form like
        atom1(args1) op1 atom2(args2) op2 atom3(args3)(args)
        :return:
        """

        def parser() -> Ast:
            ast = self._maybe_binary(self._parse_atom(), 0)
            # relational operator short-circuit implementation
            if isinstance(ast, BinaryAst):
                # left || right -> (lambda (left) {
                # if left then left else right})(left)
                binary_ast = cast(BinaryAst, ast)
                if binary_ast.operator == '||':
                    iife_param = gensym('left')
                    ast = CallAst(
                        LambdaAst(
                            '',
                            [iife_param],
                            IfAst(
                                VarAst(iife_param),
                                VarAst(iife_param),
                                binary_ast.right)),
                        [binary_ast.left])
                elif binary_ast.operator == '&&':
                    ast = IfAst(binary_ast.left, binary_ast.right, LiteralAst(False))
            return ast

        return self._maybe_call(parser)

    def _parse_call(self, func: Ast) -> CallAst:
        """
        func_name is parsed by callee before calling parse_call,
        so parse_call only need to parse func args
        :param func:
        :return:
        """
        return CallAst(
            func,
            self._delimited('(', ')', ',', self._parse_expression))

    def _maybe_call(self, parser: Callable[[], Ast]) -> Ast:
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

    def _maybe_binary(self, left: Ast, my_prec: int) -> Ast:
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
            if token.value == '=':
                binary = AssignAst(left, right)
            else:
                binary = BinaryAst(token.value, left, right)
            return self._maybe_binary(binary, my_prec)
        return left

    def __call__(self) -> ProgAst:
        return self._parse_toplevel()

    def unexpected(self):
        """
        raise exception with error msg and error location
        whenever encountered error.
        """
        self._token_stream.croak(
            f'Unexpected token: {self._token_stream.peek()}')


if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        code = f.read()
    ast = Parser(TokenStream(InputStream(code)))()
    print(ast)
