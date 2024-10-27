from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple


class Identifier(NamedTuple):
    name: str
    is_exported: bool


@dataclass
class OberonType:
    module_name: str
    name: Identifier


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

