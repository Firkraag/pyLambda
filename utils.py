#!/usr/bin/env python
# encoding: utf-8
"""
helper function
"""
from typing import Any, Dict, Callable

from ast import (AssignAst, Ast, BinaryAst, CallAst, IfAst, LambdaAst, LetAst,
                 LiteralAst, ProgAst, VarAst)


def apply_op(operator: str, left_operand: Any, right_operand: Any) -> Any:
    """
    Receive operator and operands and apply operator to operands
    We require that the operands for numeric operators be numbers,
    and that a divisor is not zero.
    For operator '&&', if a is not False, return b, otherwise return False.
    For operator '||', if a is not False, return a, otherwise return b.
    If operator is not legal, raise an exception.t
    :param operator:
    :param left_operand:
    :param right_operand:
    :return:
    """

    def num(operand):
        if isinstance(operand, (int, float)):
            return operand
        raise Exception(f"Expected int or float but got {operand}")

    def div(operand):
        if num(operand) == 0:
            raise Exception("Divide by zero")
        return operand

    mapping: Dict[str, Callable[[Any, Any], Any]] = {
        '+': lambda left, right: num(left) + num(right),
        '-': lambda left, right: num(left) - num(right),
        '*': lambda left, right: num(left) * num(right),
        '/': lambda left, right: num(left) / div(right),
        '%': lambda left, right: num(left) % div(right),
        '&&': lambda left, right: False if left is False else right,
        '||': lambda left, right: right if left is False else left,
        '<': lambda left, right: num(left) < num(right),
        '>': lambda left, right: num(left) > num(right),
        '<=': lambda left, right: num(left) <= num(right),
        '>=': lambda left, right: num(left) >= num(right),
        '==': lambda left, right: left == right,
        '!=': lambda left, right: left != right,
    }
    if operator in mapping:
        return mapping[operator](left_operand, right_operand)
    raise Exception(f"Can't apply operator {operator}")


def has_side_effect(ast: Ast) -> bool:
    """
    Since the value of ProgAst is the value of last expression, when expression
    other than last expression has no side effect, we can omit it at compile
    time.
    """
    if isinstance(ast, (LiteralAst, VarAst, LambdaAst)):
        return False
    if isinstance(ast, (CallAst, AssignAst)):
        return True
    if isinstance(ast, BinaryAst):
        return has_side_effect(ast.left) or has_side_effect(ast.right)
    if isinstance(ast, IfAst):
        return has_side_effect(ast.cond) or has_side_effect(ast.then) \
               or has_side_effect(ast.else_)
    if isinstance(ast, LetAst):
        return any(has_side_effect(vardef.define) if vardef.define else False for vardef in
                   ast.vardefs) or has_side_effect(ast.body)
    if isinstance(ast, ProgAst):
        return any(has_side_effect(prog) for prog in ast.prog)
    return True


_GENSYM = 0


def gensym(name):
    """
    Use global counter to generate unique name
    """
    global _GENSYM
    if not name:
        name = ""
    _GENSYM += 1
    return f"β_{name}{_GENSYM}"
