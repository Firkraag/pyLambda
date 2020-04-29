#!/usr/bin/env python
# encoding: utf-8
# pylint: disable=missing-docstring
from dataclasses import dataclass, field
from typing import List, Optional, Union

from environment import Environment


class Ast:
    env: Optional[Environment] = None


@dataclass
class VarDefine:
    refs: List['VarAst'] = field(default_factory=list)
    assigned: int = 0
    # kind: 1 -> global var, 2 -> lambda param var, 3 -> iife var
    # For global and iife var, constant means var is assigned only once.
    # For lambda param var, constant means param var is never assigned
    # in lambda body.
    kind: int = 2
    current_value: Optional[Ast] = None


@dataclass
class LiteralAst(Ast):
    value: Union[float, bool, str]


@dataclass
class VarAst(Ast):
    name: str
    define: Optional[VarDefine] = None


@dataclass
class VarDefAst(Ast):
    name: str
    define: Optional[Ast]


@dataclass
class LambdaAst(Ast):
    name: str
    params: List[str]
    body: Ast
    iife_params: List = field(default_factory=list)
    # never_executed: bool = True


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
    else_: Ast


@dataclass
class BinaryAst(Ast):
    operator: str
    left: Ast
    right: Ast


@dataclass
class AssignAst(Ast):
    left: Ast
    right: Ast
