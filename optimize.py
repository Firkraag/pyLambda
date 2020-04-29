"""
Optimize cps-transformed ast
Following means are applied:
1. unwrap iife, assign iife func params to iife args,
   then execute iife func body in closure.
2. If cond of IfAst is constant, we can decide which branch to execute
   at compile time
3. If two operands of BinaryAst are constants, we can get result
   at compile time
4. lambda x(args) y(args) can be optimized to y,
   a kind of tail call optimization
5. If a variable is assigned but never used, we can drop the assignment.
"""
import sys
from ast import (AssignAst, Ast, BinaryAst, CallAst, IfAst, LambdaAst,
                 LiteralAst, ProgAst, VarAst, VarDefine)
from compiler import to_js
from itertools import zip_longest
from typing import List, cast

from cps_transformer import to_cps
from environment import Environment
from input_stream import InputStream
from parse import Parser
from token_stream import TokenStream
from utils import apply_op, gensym, has_side_effect


# pylint: disable=missing-docstring
class Optimizer:
    def __init__(self):
        self.changes: bool = False
        self.closure: Ast = None

    def optimize(self, ast: Ast) -> Ast:
        """
        entry method
        """
        while True:
            self.closure: Ast = ast
            self.changes = 0
            _make_scope(ast)
            ast = self._optimize_aux(ast)
            if not self.changes:
                break
        _make_scope(ast)
        return ast

    # pylint: disable=too-many-return-statements
    def _optimize_aux(self, ast: Ast) -> Ast:
        if isinstance(ast, (LiteralAst, VarAst)):
            return ast
        if isinstance(ast, IfAst):
            return self._optimize_if_ast(ast)
        if isinstance(ast, BinaryAst):
            return self._optimize_binary_ast(ast)
        if isinstance(ast, LambdaAst):
            return self._optimize_lambda_ast(ast)
        if isinstance(ast, AssignAst):
            return self._optimize_assign_ast(ast)
        if isinstance(ast, CallAst):
            return self._optimize_call_ast(ast)
        if isinstance(ast, ProgAst):
            return self._optimize_prog_ast(ast)

        return ast

    def _optimize_prog_ast(self, ast: ProgAst) -> Ast:
        prog = ast.prog
        if not prog:
            self.changes += 1
            return LiteralAst(False)
        if len(prog) == 1:
            # self.changes += 1
            return self._optimize_aux(prog[0])
        if not has_side_effect(prog[0]):
            self.changes += 1
            return self._optimize_aux(ProgAst(prog[1:]))
        return ProgAst([self._optimize_aux(prog[0]), self._optimize_aux(ProgAst(prog[1:]))])

    def _optimize_call_ast(self, ast: CallAst) -> Ast:
        func = ast.func
        # the func part of CallAst is anonymous lambda. So the CallAst is IIFE.
        if isinstance(func, LambdaAst) and (not func.name):
            # the CallAst is inside an lambda function
            if isinstance(self.closure, LambdaAst):
                self.changes += 1
                return self._unwrap_iife(ast)

        func = self._optimize_aux(func)
        args = [self._optimize_aux(arg) for arg in ast.args]
        return CallAst(func, args)

    def _optimize_if_ast(self, ast: IfAst) -> Ast:
        cond = self._optimize_aux(ast.cond)
        then = self._optimize_aux(ast.then)
        else_ = self._optimize_aux(ast.else_)
        # if cond is constant, we can decide whether branch to execute
        # before running program.
        if isinstance(cond, LiteralAst):
            self.changes += 1
            if cond == LiteralAst(False):
                return else_
            return then
        if isinstance(cond, VarAst) and _is_constant_var(cond):
            # For lambda function params, we don't know its current value,
            # so its current value is assigned None
            if cond.define.current_value == LiteralAst(False):
                self.changes += 1
                return else_
            if isinstance(cond.define.current_value, (LiteralAst, LambdaAst)):
                self.changes += 1
                return then
        return IfAst(cond, then, else_)

    def _optimize_binary_ast(self, ast: BinaryAst) -> Ast:
        left: Ast = self._optimize_aux(ast.left)
        right: Ast = self._optimize_aux(ast.right)
        # if both operands are constance, we can get result
        # before running program.
        if isinstance(left, LiteralAst) and isinstance(right, LiteralAst):
            self.changes += 1
            result = apply_op(ast.operator, left.value, right.value)
            return LiteralAst(result)
        return BinaryAst(ast.operator, left, right)

    def _unwrap_iife(self, iife_ast: CallAst) -> ProgAst:
        """
        unwrap iife, assign iife func params to iife args,
        then execute iife func body in closure.
        :param iife_ast:
        :return:
        """
        assert isinstance(iife_ast.func, LambdaAst)
        assert isinstance(self.closure, LambdaAst)

        def rename_iife_param(param: str) -> str:
            """
            If iife param collides with closure, rename it.
            :param param:
            :return:
            """
            self.closure = cast(LambdaAst, self.closure)
            env: Environment = self.closure.env
            var_define: VarDefine = iife_func.env.get(param)
            if param in env.vars:
                param = gensym(param + '$')
            self.closure.iife_params.append(param)
            env.define(param, True)
            # change all references to iife params since we may change param names
            for ref in var_define.refs:
                ref.name = param
            return param

        iife_func = iife_ast.func
        iife_args = iife_ast.args
        assert len(iife_func.params) >= len(iife_args)
        prog: List[Ast] = [AssignAst(
            VarAst(rename_iife_param(param)),
            arg
        ) for param, arg in zip_longest(iife_func.params, iife_args, fillvalue=LiteralAst(False))]

        prog.append(self._optimize_aux(iife_func.body))
        return ProgAst(prog)

    def _optimize_assign_ast(self, ast: AssignAst) -> Ast:
        if isinstance(ast.left, VarAst):
            left: VarAst = ast.left
            right = ast.right
            # number of references is equal to assignment, which means
            # var is used only in assignment. So we can drop the assignment
            # but keep the right side.
            if len(left.define.refs) == left.define.assigned:
                # if not left.env.is_global():
                self.changes += 1
                return self._optimize_aux(right)
            if _is_constant_var(left):
                if isinstance(right, VarAst) and _is_constant_var(right):
                    self.changes += 1
                    for ref in left.define.refs:
                        ref.name = right.name
                    return self._optimize_aux(right)
        left = self._optimize_aux(ast.left)
        right = self._optimize_aux(ast.right)
        return AssignAst(left, right)

    def _optimize_lambda_ast(self, ast: LambdaAst) -> Ast:
        # lambda x(args) y(args) can be optimized to y,
        # a kind of tail call optimization
        if isinstance(ast.body, CallAst):
            # same args
            if len(ast.params) == len(ast.body.args) \
                    and all(isinstance(arg, VarAst) and arg.name == param for arg, param in
                            zip(ast.body.args, ast.params)):
                func = ast.body.func
                # If y is one of x's params, then the value of y is not decided
                # until x is called.
                if isinstance(func, VarAst) and (func.name not in ast.params):
                    # y is parameter of enclosing lambda function of x.
                    # In original version, the value of y is queried from environment
                    # when x is called. In optimized version, lambda x(args) y(args)
                    # is replaced with y, the value of y is queried when optimize occurs.
                    # So the value of y remains unchanged.
                    # Look at following example:
                    # y = some lambda
                    # foo = lambda x(args) y(args)
                    # y = another lambda
                    # foo(args)
                    #
                    # the result is (another lambda)(args)
                    #
                    # the optimized version:
                    # y = some lambda
                    # foo = y
                    # y = another lambda
                    # foo(args)
                    #
                    # the result is (some lambda)(args)

                    if func.define.assigned == 0:
                        self.changes += 1
                        return self._optimize_aux(ast.body.func)
        ast.iife_params = [
            param for param in ast.iife_params if ast.env.get(param).refs]
        save = self.closure
        self.closure = ast
        ast.body = self._optimize_aux(ast.body)
        self.closure = save
        return ast


def _is_constant_var(var_ast: VarAst) -> bool:
    """
    kind: 1 -> global var, 2 -> lambda param var, 3 -> iife var
    For global and iife var, constant means var is assigned only once.
    For lambda param var, constant means param var is never assigned
    in lambda body.
    """
    if var_ast.define.kind in (1, 3):
        return var_ast.define.assigned == 1
    return var_ast.define.assigned == 0


def _make_scope(ast: Ast) -> Environment:
    global_environment = Environment()
    ast.env = global_environment

    def _make_scope_aux(ast: Ast, env: Environment) -> None:
        if isinstance(ast, VarAst):
            def _make_scope_aux_var_ast():
                nonlocal env
                scope = env.lookup(ast.name)
                if scope is None:
                    ast.env = global_environment
                    global_environment.define(ast.name, VarDefine(kind=1))
                else:
                    ast.env = scope
                define: VarDefine = ast.env.get(ast.name)
                define.refs.append(ast)
                ast.define = define

            _make_scope_aux_var_ast()
        if isinstance(ast, LambdaAst):
            def _make_scope_aux_lambda_ast():
                nonlocal env
                ast.env = env = env.extend()
                if ast.name:
                    env.define(ast.name, VarDefine(kind=2))
                for _, param in enumerate(ast.params):
                    env.define(param, VarDefine(kind=2))
                for param in ast.iife_params:
                    env.define(param, VarDefine(kind=3))
                _make_scope_aux(ast.body, env)

            ast = cast(LambdaAst, ast)
            _make_scope_aux_lambda_ast()
        if isinstance(ast, AssignAst):
            _make_scope_aux(ast.left, env)
            _make_scope_aux(ast.right, env)
            if isinstance(ast.left, VarAst):
                ast.left.define.assigned += 1
                ast.left.define.current_value = ast.right
        if isinstance(ast, BinaryAst):
            _make_scope_aux(ast.left, env)
            _make_scope_aux(ast.right, env)

        if isinstance(ast, IfAst):
            _make_scope_aux(ast.cond, env)
            _make_scope_aux(ast.then, env)
            if ast.else_:
                _make_scope_aux(ast.else_, env)
        if isinstance(ast, ProgAst):
            for prog in ast.prog:
                _make_scope_aux(prog, env)
        if isinstance(ast, CallAst):
            _make_scope_aux(ast.func, env)
            for arg in ast.args:
                _make_scope_aux(arg, env)

    _make_scope_aux(ast, global_environment)
    return ast.env


# pylint: disable=missing-docstring
def main():
    with open(sys.argv[1]) as file:
        code = file.read()
    parser = Parser(TokenStream(InputStream(code)))
    ast = parser()
    ast = to_cps(ast, lambda ast: CallAst(
        VarAst('β_TOPLEVEL'),
        [ast],
    ))
    # print(ast)
    ast = Optimizer().optimize(ast)
    # print(ast)
    js_code = to_js(ast)
    print(js_code)

    # print(optimize(cps_code))


if __name__ == "__main__":
    main()
