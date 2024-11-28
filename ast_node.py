from enum import Enum, auto
from dataclasses import dataclass
from oberon_types import *

class Operation(Enum):
    plus = "+"
    minus = "-"
    multiple = "*"
    divide = "/"
    DIV = "DIV"
    MOD = "MOD"
    LOGICAL_OR = "OR"
    LOGICAL_AND = "&"
    LOGICAL_NOT = "~"
    UNION_FOR_SET = "+ (для множеств)"
    DIFFERENCE_FOR_SET = "- (для множеств)"
    INTERSECTION_FOR_SET = "- (для множеств)"
    SYMMETRIC_SET_DIFFERENCE = "/ (для множеств)"
    equal = "="
    unequal = "#"
    less = "<"
    less_or_equal = "<="
    greater = ">"
    greater_or_equal = ">="
    IN = "set membership"
    IS = "type test"
    procedure_call = "вызов процедуры"
    get_var_value = "получение значения переменной"
    get_const_value = "получение значения константы"


class AstNode:
    def __init__(self, value: Operation = None) -> None:
        self.value = value


class Statement:
    pass


@dataclass
class Assignment(Statement):
    var: CompositeIdentifier
    expression: AstNode


@dataclass
class ProcedureActualParameterCalculation:
    by_ref: bool
    code: AstNode


class ProcedureCall(Statement):
    actual_parameters: list[ProcedureActualParameterCalculation]
    code: AstNode


class IF(Statement):
    condition: AstNode
    code: AstNode
    else_code: AstNode


@dataclass
class IntRange:
    start: int
    end: int


@dataclass
class CaseLabel:
    value: int | IntRange | str | CompositeIdentifier


@dataclass
class CaseBranch:
    labels: list[CaseLabel]
    code: AstNode


class CASE(Statement):
    branches: list[CaseBranch]


@dataclass
class WhileBranch:
    condition: AstNode
    code: AstNode

class WHILE(Statement):
    branches: list[WhileBranch]


class REPEAT(Statement):
    condition: AstNode
    


class FOR(Statement):
    pass
