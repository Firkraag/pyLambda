#!/usr/bin/env python
# encoding: utf-8


def apply_op(op, a, b):
    """
    Receive operator and operands and apply operator to operands
    We require that the operands for numeric operators be numbers,
    and that a divisor is not zero.
    For operator '&&', if a is not False, return b, otherwise return False.
    For operator '||', if a is not False, returnt a, otherwise return b.
    If operator is not legal, raise an exception.t
    :param op:
    :param a:
    :param b:
    :return:
    """
    def num(x):
        if isinstance(x, (int, float)):
            return x
        else:
            raise Exception(f"Expected int or float but got {x}")

    def div(x):
        if num(x) == 0:
            raise Exception("Divide by zero")
        return x

    if op == "+":
        return num(a) + num(b)
    elif op == "-":
        return num(a) - num(b)
    elif op == "*":
        return num(a) * num(b)
    elif op == "/":
        return num(a) / div(b)
    elif op == "%":
        return num(a) % div(b)
    elif op == "&&":
        if a is not False:
            return b
        else:
            return False
    elif op == "||":
        if a is not False:
            return a
        return b
    elif op == "<":
        return num(a) < num(b)
    elif op == ">":
        return num(a) > num(b)
    elif op == "<=":
        return num(a) <= num(b)
    elif op == ">=":
        return num(a) >= num(b)
    elif op == "==":
        return a == b
    elif op == "!=":
        return a != b
    raise Exception(f"Can't apply operator {op}")
