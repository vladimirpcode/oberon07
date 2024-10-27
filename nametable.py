from oberon_types import *
from ast_node import *
from dataclasses import dataclass
from typing import TypeAlias


@dataclass
class ProcedureHead:
    procedure_type: ProcedureType
    name: Identifier


@dataclass
class Procedure:
    type_description: ProcedureHead
    code: AstNode


class Constant(NamedTuple):
    name: str
    value: int | float | bool | str
    constant_type: OberonType


class Variable(NamedTuple):
    name: str
    variable_type: OberonType


class ScopeOpen:
    pass

class ScopeClose:
    pass


@dataclass
class NameTableEntry:
    name: Identifier | CompositeIdentifier
    entity: Procedure | Constant | Variable | OberonType | ScopeOpen | ScopeClose


class Nametable:
    def __init__(self: str) -> None:
        self._entries: list[NameTableEntry] = list()
        self._entries.append(ScopeOpen())

    def get_global_scope_identifiers(self) -> list[NameTableEntry]:
        if len(self._entries) == 1:
            return []
        identifiers = []
        i = 1
        while i < len(self._entries) and type(self._entries[i]) not in [ScopeOpen, ScopeClose]:
            identifiers.append(self._entries[i])
            i += 1
        return identifiers

    def get_local_scope_identifiers(self) -> list[NameTableEntry]:
        if len(self._entries) == 1:
            return []
        i = len(self._entries) - 1
        if self._entries[i] is ScopeClose:
            i -= 1
        identifiers = []
        while i > 0 and self._entries[i] is not ScopeOpen:
            identifiers.append(self._entries[i])
            i -= 1
        return identifiers

    def get_all_identifiers_for_current_scope(self) -> list[NameTableEntry]:
        return self.get_global_scope_identifiers() + self.get_local_scope_identifiers()




