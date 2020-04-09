#!/usr/bin/env python
# encoding: utf-8
from dataclasses import dataclass
from typing import Union, Optional, List


class Ast:
    pass


@dataclass
class LiteralAst(Ast):
    value: Union[float, bool, str]


@dataclass
class VarAst(Ast):
    name: str


@dataclass
class VarDefAst(Ast):
    name: str
    define: Optional[Ast]


@dataclass
class LambdaAst(Ast):
    name: str
    params: List[str]
    body: Ast


@dataclass
class LetAst(Ast):
    vardefs: List[VarDefAst]
    body: Ast


@dataclass
class CallAst(Ast):
    func: Ast
    args: List[Ast]


@dataclass
class ProgAst(Ast):
    prog: List[Ast]


@dataclass
class IfAst(Ast):
    cond: Ast
    then: Ast
    else_: Optional[Ast]


@dataclass
class BinaryAst(Ast):
    operator: str
    left: Ast
    right: Ast


@dataclass
class AssignAst(Ast):
    left: Ast
    right: Ast
