from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple


class Identifier(NamedTuple):
    name: str
    is_exported: bool
    
    def __str__(self) -> str:
        return self.name + ("*" if self.is_exported else "")


@dataclass
class OberonType:
    module_name: str
    type_name: Identifier


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
    

def identifier_to_str(identifier: Identifier | CompositeIdentifier) -> str:
    if type(identifier) is Identifier:
        return identifier.name
    elif type(identifier) is CompositeIdentifier:
        if identifier.parent_name is None:
            raise ValueError("родительское имя составного идентификатора не может быть пустым")
        if identifier.child_name is not None and identifier.child_name != "":
            return identifier.parent_name + "." + identifier.child_name
        else:
            return identifier.parent_name
    else:
        raise ValueError(f"Неподходящий тип идентификатора - {str(type(identifier))}")