#!/usr/bin/env python
# encoding: utf-8
from token_stream import TokenStream


class Parser(object):
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

    def skip_punc(self, ch: str) -> None:
        if self.is_punc(ch):
            self._token_stream.next()
        else:
            self._token_stream.croak('Expecting punctuation: \"' + ch + "\"")

    def is_punc(self, ch: str) -> bool:
        token = self._token_stream.peek()
        return token and token == {'type': 'punc', 'value': ch}

    def skip_kw(self, ch: str) -> None:
        if self.is_kw(ch):
            self._token_stream.next()
        else:
            self._token_stream.croak('Expecting keyword: \"' + ch + "\"")

    def is_kw(self, ch: str) -> bool:
        token = self._token_stream.peek()
        return (token is not None) and token == {'type': 'kw', 'value': ch}

    def skip_op(self, ch: str) -> None:
        if self.is_op(ch):
            self._token_stream.next()
        else:
            self._token_stream.croak('Expecting operator: \"' + ch + "\"")

    def is_op(self, ch: str) -> bool:
        token = self._token_stream.peek()
        return (token is not None) and token == {'type': 'op', 'value': ch}

    def delimited(self, start: str, stop: str, separator: str, parser) -> list:
        a = []
        first = True
        self.skip_punc(start)
        while not self._token_stream.eof():
            if self.is_punc(stop):
                break
            if first:
                first = False
            else:
                self.skip_punc(separator)
            if self.is_punc(stop):
                break
            a.append(parser())
        self.skip_punc(stop)
        return a

    def parse_lambda(self) -> dict:
        return {
            'type': 'lambda',
            'name': self._token_stream.next()['value'] if self._token_stream.peek()['type'] == 'var' else None,
            'vars': self.delimited("(", ")", ",", self.parse_varname),
            'body': self.parse_expression(),
        }

    def parse_let(self) -> dict:
        self.skip_kw('let')
        if self._token_stream.peek()['type'] == 'var':
            name = self._token_stream.next()['value']
            defs = self.delimited('(', ')', ',', self.parse_vardef)
            return {
                'type': 'call',
                'func': {
                    'type': 'lambda',
                    'name': name,
                    'vars': [define['name'] for define in defs],
                    'body': self.parse_expression(),
                },
                'args': [define['def'] for define in defs],
            }
        else:
            d = {
                'type': 'let',
                'vars': self.delimited('(', ')', ',', self.parse_vardef),
                'body': self.parse_expression(),
            }
            return d

    def parse_vardef(self):
        name = self.parse_varname()
        define = False
        if self.is_op('='):
            self._token_stream.next()
            define = self.parse_expression()
        return {'name': name, 'def': define}

    def parse_varname(self) -> dict:
        token = self._token_stream.next()
        if token['type'] != 'var':
            self._token_stream.croak('Expecting variable name')
        return token['value']

    def parse_toplevel(self) -> dict:
        prog = []
        while not self._token_stream.eof():
            prog.append(self.parse_expression())
            if not self._token_stream.eof():
                self.skip_punc(";")
        return {
            'type': 'prog',
            'prog': prog,
        }

    def __call__(self, *args, **kwargs):
        return self.parse_toplevel()

    def parse_if(self) -> dict:
        self.skip_kw("if")
        cond = self.parse_expression()
        if not self.is_punc('{'):
            self.skip_kw('then')
        then = self.parse_expression()
        ret = {
            'type': 'if',
            'cond': cond,
            'then': then,
        }
        # print(self._token_stream.peek())
        if self.is_kw('else'):
            self.skip_kw('else')
            ret['else'] = self.parse_expression()
        return ret

    def parse_atom(self) -> dict:
        def parser() -> dict:
            if self.is_punc('('):
                self.skip_punc('(')
                exp = self.parse_expression()
                self.skip_punc(')')
                return exp
            if self.is_punc('{'):
                return self.parse_prog()
            if self.is_kw('if'):
                return self.parse_if()
            if self.is_kw('let'):
                return self.parse_let()
            if self.is_kw('true') or self.is_kw('false'):
                return self.parse_bool()
            if self.is_kw('lambda') or self.is_kw('λ'):
                self._token_stream.next()
                return self.parse_lambda()
            token = self._token_stream.next()
            if token['type'] in {'var', 'num', 'str'}:
                return token
            self.unexpected()

        return self.maybe_call(parser)

    def parse_prog(self) -> dict:
        prog = self.delimited("{", "}", ";", self.parse_expression)
        if len(prog) == 0:
            return {
                'type': 'bool', 'value': False,
            }
        elif len(prog) == 1:
            return prog[0]
        else:
            return {'type': 'prog', 'prog': prog}

    def parse_bool(self) -> dict:
        return {
            'type': 'bool',
            'value': self._token_stream.next()['value'] == 'true',
        }

    def parse_expression(self) -> dict:
        def parser():
            return self.maybe_binary(self.parse_atom(), 0)

        return self.maybe_call(parser)

    def parse_call(self, func_name: str) -> dict:
        return {
            'type': 'call',
            'func': func_name,
            'args': self.delimited('(', ')', ',', self.parse_expression)
        }

    def maybe_call(self, parser) -> dict:
        expr = parser()
        return self.parse_call(expr) if self.is_punc("(") else expr

    def maybe_binary(self, left: dict, my_prec: int) -> dict:
        token = self._token_stream.peek()
        if token is None or token['type'] != 'op':
            return left
        his_prec = self.PRECEDENCE[token['value']]
        if his_prec > my_prec:
            self._token_stream.next()
            right = self.maybe_binary(self.parse_atom(), his_prec)
            binary = {
                'type': 'assign' if token['value'] == '=' else 'binary',
                'operator': token['value'],
                'left': left,
                'right': right
            }
            return self.maybe_binary(binary, my_prec)
        return left

    def unexpected(self):
        self._token_stream.croak('Unexpected token: ' + str(self._token_stream.peek()))
