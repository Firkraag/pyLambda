#!/usr/bin/env python
# encoding: utf-8
from typing import Any, Dict, Callable


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
