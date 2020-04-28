#!/usr/bin/env python
# encoding: utf-8
"""
Sturcture to hold variable info when we run program and optimize the program
"""
from typing import Optional, Any, Dict, TypeVar

Type = TypeVar('T')


class Environment:
    def __init__(self, parent: Optional['Environment'] = None):
        self.vars: Dict[str, Any] = {}
        self.parent: Optional['Environment'] = parent

    def is_global(self):
        """
        whether self is a global environment
        :return:
        """
        return self.parent is None

    def extend(self) -> 'Environment':
        """
        create a subscope
        :return:
        """
        return Environment(self)

    def lookup(self, var_name: str) -> Optional['Environment']:
        """
        Find the scope where the variable with the given name is defined
        If not found, return None.
        :rtype:
        :param var_name:
        :return:
        """
        scope = self
        while scope is not None:
            if var_name in scope.vars:
                return scope
            scope = scope.parent

    def define(self, var_name: str, value: Type) -> Type:
        """
        Create a variable in the current scope
        :param var_name:
        :param value:
        :return:
        """
        self.vars[var_name] = value
        return value

    def get(self, var_name: str) -> Any:
        """
        Lookup the actual scope where the variable is defined and
        get the value of a variable in that scope.
        If variable is not defined, raise a exception.
        :param var_name:
        :return:
        """
        environment = self.lookup(var_name)
        if environment is None:
            raise Exception(f"Undefined variable {var_name}")
        return environment.vars[var_name]

    def set(self, var_name: str, value: Any) -> Any:
        """
        Lookup the actual scope where the variable is defined and
        set the value of a variable in that scope.
        If variable is defined, set variable, else if variable is not defined
        but current scope is global scope, define variable in global scope,
        otherwise, raise a exception.
        :param var_name:
        :param value:
        :return:
        """
        scope = self.lookup(var_name)
        if scope is not None:
            scope.vars[var_name] = value
        # not global environment
        elif self.parent is not None:
            raise Exception(f"Undefined variable {var_name}")
        # No parent, so current scope is global scope
        else:
            self.vars[var_name] = value
        return value
