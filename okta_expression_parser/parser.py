# pyright: reportUndefinedVariable=false
import logging
from os import environ
from sys import stdout
from typing import Any, Callable, Dict, List, Sequence
from types import ModuleType

import sly
from sly.yacc import YaccProduction

from . import expression_classes as _default_expression_classes
from .lexer import ExpressionLexer


class ExpressionParser(sly.Parser):
    if debug_file := environ.get("OKTA_EXPRESSION_PARSER_LOG_FILE"):
        #: Writes grammar rules to a file for debugging
        debugfile: str = environ.get(debug_file)

    #: Gets the token list from the lexer (required)
    tokens: Sequence = ExpressionLexer.tokens

    #: Defines precendence of operators
    precedence = (
        ("left", OR),  # noqa: 821
        ("left", AND),  # noqa: 821
        ("right", NOT),  # noqa: 821
        ("nonassoc", EQ, NE),  # noqa: 821
    )

    def __init__(
        self,
        group_ids: List[str] = [],
        user_profile: Dict[str, Any] = {},
        log_to_stdout: bool = False,
        log_level: str = "INFO",
        expression_classes: ModuleType = _default_expression_classes,
    ) -> None:
        #: A module containing classes used in expressions, such as `Arrays` or `String`
        self._expression_classes = expression_classes
        self.__group_ids: str = group_ids
        self.__user_profile: str = user_profile
        self.logger: logging.Logger = logging.getLogger()

        self.logger.setLevel(log_level)

        if log_to_stdout:
            self.logger.addHandler(logging.StreamHandler(stream=stdout))

    def parse(self, expression: str):
        return super().parse(ExpressionLexer().tokenize(expression))

    @_("operand EQ operand")  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:
        operand0 = p.operand0
        operand1 = p.operand1
        return operand0 == operand1

    @_("path EQ operand")  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:
        path = p.path
        value = p.operand

        return path == value

    @_("operand NE operand")  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1
        return operand0 != operand1

    @_("operand GTE operand")  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1
        return type(operand0) == type(operand1) and operand0 >= operand1

    @_("operand LTE operand")  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1
        return type(operand0) == type(operand1) and operand0 <= operand1

    @_("operand LT operand")  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1
        return type(operand0) == type(operand1) and operand0 < operand1

    @_("operand GT operand")  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1
        return type(operand0) == type(operand1) and operand0 > operand1

    @_("condition AND condition")  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:  # noqa: 811
        condition0 = p.condition0
        condition1 = p.condition1
        return condition0 and condition1

    @_("condition OR condition")  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:  # noqa: 811
        condition0 = p.condition0
        condition1 = p.condition1
        return condition0 or condition1

    @_("NOT condition")  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:  # noqa: 811
        condition = p.condition
        return not condition

    @_("NOT path")  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:  # noqa: 811
        return not p.path

    @_('"(" condition ")"')  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:  # noqa: 811
        condition = p.condition
        return condition

    @_('arg_list "," operand')  # noqa: 821
    def arg_list(self, p: YaccProduction) -> List[Any]:  # noqa: 811
        arg_list = p.arg_list
        operand = p.operand
        return [*arg_list, operand]

    @_('operand "," arg_list')  # noqa: 821
    def arg_list(self, p: YaccProduction) -> List[Any]:  # noqa: 811
        arg_list = p.arg_list
        operand = p.operand
        return [operand, *arg_list]

    @_('operand "," operand')  # noqa: 821
    def arg_list(self, p: YaccProduction) -> List[Any]:  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1
        return [operand0, operand1]

    @_("NULL")
    def operand(self, p: YaccProduction) -> None:
        return None

    @_("INT")  # noqa: 821
    def operand(self, p: YaccProduction) -> int:  # noqa: 811
        return int(p.INT)

    @_("BOOL")
    def operand(self, p: YaccProduction) -> bool:
        val = p.BOOL.lower()
        return val == "true"

    @_('"{" arg_list "}"')
    def array(self, p: YaccProduction) -> List[Any]:
        return p.arg_list

    @_('"{" operand "}"')
    def array(self, p: YaccProduction) -> List[Any]:
        print("array - operand")
        return [p.operand]

    @_("STRING")  # noqa: 821
    def operand(self, p: YaccProduction) -> str:  # noqa: 811
        val = p.STRING
        if val.startswith('"'):
            val = val[1:-1]

        return val

    @_("path")  # noqa: 821
    def operand(self, p: YaccProduction) -> Any:  # noqa: 811
        return p.path

    @_("USER")
    def path(self, _) -> Dict[str, Any]:
        return self.__user_profile

    @_('path "." NAME')  # noqa: 821
    def path(self, p: YaccProduction) -> Any:  # noqa: 811
        path = p.path
        NAME = p.NAME

        if isinstance(path, dict):
            res = path.get(NAME)
        else:
            res = path

        if isinstance(res, str):
            res = res.replace('"', "")

        return res

    @_("NAME")  # noqa: 821
    def path(self, p: YaccProduction) -> Any:  # noqa: 811
        NAME = p.NAME
        if not hasattr(p, "path"):
            path = {}

        return path.get(NAME) if path is not None else None

    @_("cls")
    def condition(self, p: YaccProduction) -> Any:
        """
        Returns the result of the call to a class method called from
        `self._expression_classes`
        """
        return p.cls

    @_("CLASS")
    def cls(self, p: YaccProduction) -> type:
        """Returns a class from `self._expression_classes`"""

        try:
            return getattr(self._expression_classes, p.CLASS)
        except AttributeError:
            raise NotImplemented(
                f"Class {p.CLASS} has not been implemented in the parser"
            )

    @_('cls "." NAME')
    def cls(self, p: YaccProduction) -> Callable:
        """Returns a callable from `cls`, which is a class from `self._expression_classes`"""
        method = getattr(p.cls, p.NAME)
        return method

    @_('path "," operand')
    def path_value_args(self, p: YaccProduction) -> List[Any]:
        """Appends and operand to list to be passed as arguments to a tokenized method"""
        path = p.path
        val = p.operand
        return [path, val]

    @_('array "," operand')
    def array_value_args(self, p: YaccProduction) -> List[Any]:
        """
        Defines a method signature consisting of an array token as the first argument
        and a discrete operand token as the second
        """
        return [p.array, p.operand]

    @_('cls "(" path_value_args ")"')
    @_('cls "(" array_value_args ")"')
    def cls(self, p: YaccProduction) -> Any:
        """
        Executes and returns the value from a callable defined in a token as `cls.NAME`,
        passing a list or an array of args
        """
        method = p.cls

        if hasattr(p, "path_value_args"):
            args = p.path_value_args
        else:
            args = p.array_value_args
        res = method(*args)
        return res

    @_('cls "(" operand ")"')
    def cls(self, p: YaccProduction) -> Any:
        """
        Executes and returns the value from a callable defined in a token as `cls.NAME`,
        passing a single arg
        """
        method = p.cls
        if isinstance(p.operand, list):
            res = method(*p.operand)
        else:
            res = method(p.operand)
        return res

    @_('MEMBEROFANY "(" operand ")"')
    @_('MEMBEROFANY "(" arg_list ")"')
    def condition(self, p: YaccProduction):
        """
        Tests if a user is a member of one or many groups
        """
        if not self.__group_ids:
            return False

        if not hasattr(p, "arg_list"):
            res = p.operand in self.__group_ids
        else:
            arg_list = p.arg_list
            res = bool(list(set(self.__group_ids) & set(arg_list)))
        return res

    @_('MEMBEROF "(" operand ")"')
    def condition(self, p: YaccProduction):
        """Tests if a user is a member of a specific group"""

        if not self.__group_ids:
            return False

        # return p.operand.lower() in self.__group_ids
        return p.operand in self.__group_ids

    @_("condition error")  # noqa: 821
    def operand(self, x):  # noqa: 811
        raise SyntaxError(
            f"Unexpected token '{x.error.value}' on line {x.error.lineno}"
        )
