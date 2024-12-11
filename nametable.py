from oberon_types import *
from ast_node import *
from dataclasses import dataclass
from typing import TypeAlias


class Constant(NamedTuple):
    name: str
    value: int | float | bool | str
    constant_type: OberonType


class Variable(NamedTuple):
    name: str
    variable_type: OberonType


class ProcedureHead:
    def __init__(self, procedure_type=None, name=None) -> None:
        self.procedure_type: ProcedureType = ProcedureType(None, None, NoReturnType, list())
        self.name: Identifier = name

    def __str__(self) -> str:
        result = f"PROCEDURE {str(self.name)}"
        if len(self.procedure_type.parameters) != 0:
            result += "("
            for param in self.procedure_type.parameters:
                if param.by_ref:
                    result += "VAR "
                result += f"{param.name}: {param.param_type.type_name},"
            result = result[:-1]
            result += ")"
            if not isinstance(self.procedure_type.return_type, NoReturnType):
                result += f": {self.procedure_type.return_type.type_name}"
        return result


class ProcedureBody:
    def __init__(self, code=None, variables=list(), constants=list(), types=list()) -> None:
        self.code: AstNode = code
        self.variables: list[Variable] = variables
        self.constants: list[Constant] = constants
        self.types: list[OberonType] = types


class Procedure:
    def __init__(self, head=ProcedureHead(), body=ProcedureBody()) -> None:
        self.head: ProcedureHead = head
        self.body: ProcedureBody = body
    def __str__(self) -> str:
        return f"{str(self.head)}"


class ScopeOpen:
    pass

class ScopeClose:
    pass


@dataclass
class NameTableEntry:
    name: Identifier | CompositeIdentifier
    entity: Procedure | Constant | Variable | OberonType | ScopeOpen | ScopeClose | ProcedureParameter
    def __str__(self) -> str:
        return str(self.entity)


class Nametable:
    def __init__(self: str) -> None:
        self._entries: list[NameTableEntry] = list()
        self.open_scope()

    def get_global_scope_identifiers(self) -> list[NameTableEntry]:
        print(self)
        def skip_local_scope(nametable: Nametable, index: int) -> int:
            if not isinstance(nametable._entries[index].entity, ScopeOpen):
                raise Exception("ожидалось ScopeOpen")
            index += 1
            while index < len(nametable._entries) and not isinstance(nametable._entries[index].entity, ScopeClose):
                index += 1
            if index < len(nametable._entries):
                index += 1
            return index

        if len(self._entries) == 1:
            return []
        identifiers = []
        i = 1
        while i < len(self._entries):
            if isinstance(self._entries[i].entity, ScopeOpen):
                i = skip_local_scope(self, i)
            if i >= len(self._entries):
                return identifiers
            if isinstance(self._entries[i].entity, ScopeClose):
                return identifiers
            identifiers.append(self._entries[i])
            i += 1
        return identifiers

    def get_local_scope_identifiers(self) -> list[NameTableEntry]:
        if len(self._entries) == 1:
            return []
        i = len(self._entries) - 1
        if type(self._entries[i].entity) is ScopeClose:
            i -= 1
        identifiers = []
        while i > 0 and not isinstance(self._entries[i].entity, ScopeOpen):
            if not isinstance(self._entries[i].entity, ScopeClose):
                identifiers.append(self._entries[i]) 
            i -= 1
        return identifiers

    def get_all_identifiers_for_current_scope(self) -> list[NameTableEntry]:
        return self.get_global_scope_identifiers() + self.get_local_scope_identifiers()
    
    def open_scope(self):
        self._entries.append(NameTableEntry(None, ScopeOpen()))

    def close_scope(self):
        self._entries.append(NameTableEntry(None, ScopeClose()))

    def add_entry(self, new_entry: NameTableEntry):
        self._entries.append(new_entry)

    def __str__(self) -> str:
        result = "--------------------------------------------\n"
        tab_index = -1
        for entry in self._entries:
            if isinstance(entry.entity, ScopeOpen):
                tab_index += 1
            elif isinstance(entry.entity, ScopeClose):
                tab_index -= 1
            else:
                result += "  " * tab_index  + str(entry) + "\n"
        
        result += "--------------------------------------------\n"
        return result


