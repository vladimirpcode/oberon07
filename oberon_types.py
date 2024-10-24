from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple


class OberonType:
    pass


@dataclass
class ArrayType(OberonType):
    element_type: OberonType
    size: int


class BasicTypesEnum(Enum):
    BOOLEAN = "BOOLEAN",
    CHAR = "CHAR",
    INTEGER = "INTEGER",
    REAL = "REAL",
    BYTE = "BYTE",
    SET = "SET"


class BasicType(OberonType):
    basic_type: BasicTypesEnum


class Identifier(NamedTuple):
    name: str
    is_exported: bool


@dataclass
class RecordField:
    identifier: Identifier
    field_type: OberonType


@dataclass
class RecordType(OberonType):
    base_type: OberonType
    fields: list[RecordField]


@dataclass
class PointerType(OberonType):
    type_of_pointer: OberonType


class NoReturnType(OberonType):
    pass


@dataclass
class ProcedureParameter:
    name: str
    param_type: OberonType
    by_ref: bool


@dataclass
class ProcedureType(OberonType):
    return_type: OberonType
    parameters: list[ProcedureParameter]


class CompositeIdentifier(NamedTuple):
    parent_name: str
    child_name: str


class Constant(NamedTuple):
    name: str
    value: int | float | bool | str
    constant_type: OberonType

