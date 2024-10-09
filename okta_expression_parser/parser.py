# pyright: reportUndefinedVariable=false
import logging
from os import environ
from re import match
from sys import stdout
from typing import Any, Dict, List, Sequence
from types import ModuleType

import sly
from sly.yacc import YaccProduction

from . import expression_classes as _default_expression_classes
from .expression_classes.arrays import _ArrayType
from .lexer import ExpressionLexer


# Sly doesn't really facilitate configuring logging from the caller, so we're going to
# suppress all logging below the level specified in the LOG_LEVEL environment variable.
log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "EXCEPTION"]

log_level = environ.get("LOG_LEVEL", "ERROR")

log_rank = log_levels.index(log_level)

for level_name in list(reversed(log_levels))[:log_rank +1]:
    log_attr = level_name.lower()
    setattr(sly.yacc.SlyLogger, log_attr, lambda self, msg, *args, **kwargs: None)


class ExpressionParser(sly.Parser):
    #: Writes grammar rules to a file for debugging
    debugfile = environ.get("OKTA_EXPRESSION_PARSER_LOG_FILE")

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
        log_level: str = environ.get("LOG_LEVEL", "ERROR"),
        expression_classes: ModuleType = _default_expression_classes,
        group_data: dict = {},
    ) -> None:
        #: A module containing classes used in expressions, such as `Arrays` or `String`
        self._expression_classes = expression_classes

        # Required for doing translations between group ID's and other group attributes.
        # Without passing group_data into the parser all `Group` methods will return empty
        if (
            group_data
            and hasattr(self._expression_classes, "Groups")
            and type(self._expression_classes.Groups) == type
        ):
            self._expression_classes.Groups.group_data = group_data

        #: A dict, with Group ID's as the keys and group data as the values. Used for operations that require more context than just the group ID.
        self.group_data = group_data

        self.__group_ids: str = group_ids
        self.__user_profile: str = user_profile
        self.logger: logging.Logger = logging.getLogger()

        self.logger.setLevel(log_level)

        if log_to_stdout:
            self.logger.addHandler(logging.StreamHandler(stream=stdout))

    def parse(self, expression: str):
        return super().parse(ExpressionLexer().tokenize(expression))

    @_("operand")  # noqa: 821
    @_("condition")  # noqa: 821
    def result(self, p: YaccProduction) -> bool:  # noqa: 811
        res = p.condition if hasattr(p, "condition") else p.operand
        return res

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

    @_('"(" condition ")"')  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:  # noqa: 811
        return p.condition

    @_('"(" operand ")"')  # noqa: 821
    def operand(self, p: YaccProduction) -> bool:  # noqa: 811
        return p.operand

    @_("condition AND condition")  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:  # noqa: 811
        return p.condition0 and p.condition1

    @_("operand AND operand")  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:  # noqa: 811
        return p.operand0 and p.operand1

    @_("operand AND condition")  # noqa: 821
    @_("condition AND operand")  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:  # noqa: 811
        return p.condition and p.operand

    @_("condition OR condition")  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:  # noqa: 811
        return p.condition0 or p.condition1

    @_("operand OR operand")  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:  # noqa: 811
        return p.operand0 or p.operand1

    @_("operand OR condition")  # noqa: 821
    @_("condition OR operand")  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:  # noqa: 811
        return p.condition or p.operand

    @_("NOT condition")  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:  # noqa: 811
        condition = p.condition
        return not condition

    @_("NOT operand")  # noqa: 821
    def condition(self, p: YaccProduction) -> bool:  # noqa: 811
        return not p.operand

    @_('operand "," operand')  # noqa: 821
    def operand(self, p: YaccProduction) -> List[Any]:  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1

        if isinstance(operand0, tuple) and isinstance(operand1, tuple):
            res = operand0 + operand1
        elif isinstance(operand0, tuple) and not isinstance(operand1, tuple):
            res = operand0 + (operand1,)
        elif not isinstance(operand0, tuple) and isinstance(operand1, tuple):
            res = (operand0,) + operand1
        else:
            res = (operand0, operand1)
        return res

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

    @_("array")
    def operand(self, p: YaccProduction) -> List[Any]:
        return _ArrayType(p.array)

    @_('"{" operand "}"')
    def array(self, p: YaccProduction) -> List[Any]:
        if isinstance(p.operand, Sequence):
            return _ArrayType(p.operand)

        return _ArrayType([p.operand])

    @_('array "," operand')
    def operand(self, p: YaccProduction) -> List[Any]:
        # if isinstance(p.operand, tuple):

        if isinstance(p.operand, tuple):
            return (p.array,) + p.operand

        return (p.array, p.operand)

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

    @_("NAME")  # noqa: 821
    def path(self, p: YaccProduction) -> Any:  # noqa: 811
        NAME = p.NAME

        if not hasattr(p, "path"):
            path = {}

        return path.get(NAME) if path is not None else None

    @_('path "." NAME')  # noqa: 821
    def operand(self, p: YaccProduction) -> Any:  # noqa: 811
        path = p.path
        NAME = p.NAME

        if isinstance(path, dict):
            res = path.get(NAME)
        else:
            res = path

        if isinstance(res, str):
            res = res.replace('"', "")

        return res

    @_("cls")
    def operand(self, p: YaccProduction) -> Any:
        """
        Returns a class from `self._expression_classes`
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

    @_('cls "." NAME "(" operand ")"')
    @_('cls "." NAME "(" path ")"')
    def operand(self, p: YaccProduction) -> Any:
        """Calls a method from `cls`, which is a class from `self._expression_classes`"""
        method = getattr(p.cls, p.NAME)

        if hasattr(p, "operand"):
            val = p.operand
        else:
            val = p.path

        if isinstance(val, tuple):
            res = method(*val)

        else:
            res = method(val)

        return res

    @_('cls "." NAME "(" operand ")"')
    @_('cls "." NAME "(" path ")"')
    def condition(self, p: YaccProduction) -> bool:
        """Calls a method from `cls`, which is a class from `self._expression_classes`"""
        method = getattr(p.cls, p.NAME)

        if hasattr(p, "operand"):
            val = p.operand
        else:
            val = p.path

        if isinstance(val, tuple):
            res = method(*val)

        else:
            res = method(val)

        return res

    @_('MEMBEROFANY "(" operand ")"')
    def condition(self, p: YaccProduction):
        """
        Tests if a user is a member of one or many groups
        """
        if not self.__group_ids:
            return False

        val = p.operand

        if not isinstance(val, tuple):
            val = [val]

        res = list(set(self.__group_ids) & set(val))

        return bool(res)

    @_('MEMBEROF "(" operand ")"')
    def condition(self, p: YaccProduction):
        """Tests if a user is a member of a specific group"""

        if not self.__group_ids:
            return False

        return p.operand in self.__group_ids

    @_('MEMBEROFNAME "(" operand ")"')
    def condition(self, p: YaccProduction):
        """Tests if a user is a member of a group with a specific name"""

        matches = [
            v for k, v in self.group_data.items() if v["profile"]["name"] == p.operand
        ]

        return bool(matches)

    @_('MEMBEROFGROUPSTARTSWITH "(" operand ")"')
    def condition(self, p: YaccProduction):
        """Tests if a user is a member of a group with a specific name"""

        matches = [
            v
            for k, v in self.group_data.items()
            if v["profile"]["name"].startswith(p.operand)
        ]

        return bool(matches)

    @_('MEMBEROFGROUPCONTAINS "(" operand ")"')
    def condition(self, p: YaccProduction):
        """Tests if a user is a member of a group with a specific name"""

        matches = [
            v for k, v in self.group_data.items() if p.operand in v["profile"]["name"]
        ]

        return bool(matches)

    @_('MEMBEROFGROUPNAMEREGEX "(" operand ")"')
    def condition(self, p: YaccProduction):
        """Tests if a user is a member of a group with a specific name"""

        for _, group in self.group_data.items():
            if match(p.operand, group["profile"]["name"]):
                return True

        return False

    @_("operand QUESTION_MARK operand COLON operand")  # noqa: 821
    @_("condition QUESTION_MARK operand COLON operand")  # noqa: 821
    def operand(self, p: YaccProduction) -> Any:  # noqa: 811
        condition = p.condition if hasattr(p, "condition") else p.operand0
        if_true = p.operand0 if hasattr(p, "condition") else p.operand1
        if_false = p.operand1 if hasattr(p, "condition") else p.operand2

        return if_true if condition else if_false

    @_("condition error")  # noqa: 821
    def operand(self, x):  # noqa: 811
        raise SyntaxError(
            f"Unexpected token '{x.error.value}' on line {x.error.lineno}"
        )
