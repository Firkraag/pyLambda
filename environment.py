#!/usr/bin/env python
# encoding: utf-8


class Environment(object):
    def __init__(self, parent=None):
        self._vars = {}
        self._parent = parent

    def extend(self):
        """
        create a subscope
        :return:
        """
        return Environment(self)

    def lookup(self, var_name: str):
        """
        Find the scope where the variable with the given name is defined
        If not found, return None.
        :param var_name:
        :return:
        """
        scope = self
        while scope:
            if var_name in scope._vars:
                return scope
            scope = scope._parent

    def define(self, var_name: str, value: object) -> None:
        """
        Create a variable in the current scope
        :param var_name:
        :param value:
        :return:
        """
        self._vars[var_name] = value

    def get(self, var_name: str) -> object:
        """
        Get the current value of a variable. Raise a exception if the variable is not defined
        :param var_name:
        :return:
        """
        scope = self
        while scope:
            if var_name in scope._vars:
                return scope._vars[var_name]
            scope = scope._parent
        raise Exception(f"Undefined variable {var_name}")

    def set(self, var_name: str, value: object) -> None:
        """
        Lookup the actual scope where the variable is defined and set the value of a variable in that scope.
        If variable is not defined and current scope is global scope, define variable in global otherwise.
        Otherwise, raise a exception.
        :param var_name: 
        :param value: 
        :return: 
        """
        scope = self.lookup(var_name)
        if scope:
            scope._vars[var_name] = value
        elif self._parent:
            raise Exception(f"Undefined variable {var_name}")
        # No parent, so current scope is global scope
        else:
            self._vars[var_name] = value
