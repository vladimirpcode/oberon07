from lexer import Lexer, Lex
from typing import NamedTuple
from oberon_types import *


class Identifier(NamedTuple):
    name: str
    is_exported: bool


class CompositeIdentifier(NamedTuple):
    parent_name: str
    child_name: str


class Constant(NamedTuple):
    name: str
    value: int | float | bool | str
    constant_type: OberonType


class Parser:
    def __init__(self, program: str) -> None:
        self._lexer = Lexer(program)
        self._parse_module()

    def _raise_expected_exception(self, expected: str):
        raise Exception(f"Ожидалось {expected}, но {self._lexer.lex.value[0]}")

    def _check(self, lex: Lex):
        if self._lexer.lex != lex:
            self._raise_expected_exception(lex.value[0])
        self._lexer.get_next()

        
    def _parse_sring(self) -> str:
        if self._lexer.lex != Lex.string:
            self._raise_expected_exception("строка")
        s = self._lexer.value
        self._lexer.get_next()
        return s

    def _parse_number(self) -> float | int:
        if self._lexer.lex != Lex.number:
            self._raise_expected_exception("число")
        number = self._lexer.value
        self._lexer.get_next()
        return number

    def _parse_ident(self) -> str:
        if self._lexer.lex != Lex.ident:
            self._raise_expected_exception("идентификатор")
        name = self._lexer.value
        self._lexer.get_next()
        return name

    def _parse_identdef(self) -> Identifier:
        ident = self._parse_ident()
        is_exported = False
        if self._lexer.lex == Lex.multiple:
            self._lexer.get_next()
            is_exported = True
        return Identifier(ident, is_exported)
    
    def _parse_qualident(self) -> CompositeIdentifier:
        parent_name = self._parse_ident()
        child_name = ""
        if self._lexer.lex == Lex.dot:
            self._lexer.get_next()
            child_name = self._parse_ident()
        return CompositeIdentifier(parent_name, child_name)

    def _parse_module(self):
        self._check(Lex.MODULE)
        module_name = self._parse_ident()
        self._check(Lex.semicollon)
        if self._lexer.lex == Lex.IMPORT:
            self._parse_import_list()
        self._parse_declaration_sequence()
        if self._lexer.lex == Lex.BEGIN:
            self._lexer.get_next()
            self._parse_statement_sequence()
        self._check(Lex.END)
        if self._parse_ident() != module_name:
            self._raise_expected_exception(f"имя модуля {module_name}")
        self._lexer.get_next()
        self._check(Lex.dot)

    def _parse_import_list(self):
        self._check(Lex.IMPORT)
        self._parse_import()
        while self._lexer.lex == Lex.comma:
            self._lexer.get_next()
            self._parse_import()
        self._check(Lex.semicollon)

    def _parse_import(self):
        if self._lexer.lex != Lex.ident:
            self._raise_expected_exception("ожидалось имя импортируемого модуля")
        imported_module_name = self._lexer.value
        self._lexer.get_next()
        if self._lexer.lex == Lex.assignment:
            self._lexer.get_next()
            if self._lexer.lex != Lex.ident:
                self._raise_expected_exception("ожидалось альтернативное имя импортируемого модуля")
            alias = self._lexer.value

    def _parse_declaration_sequence(self):
        if self._lexer.lex == Lex.CONST:
            self._lexer.get_next()
            while self._lexer.lex == Lex.ident:
                self.parse_const_declaration()
                self._check(Lex.semicollon)
        if self._lexer.lex == Lex.TYPE:
            self._lexer.get_next()
            while self._lexer.lex == Lex.ident:
                self.parse_type_declaration()
                self._check(Lex.semicollon)
        if self._lexer.lex == Lex.VAR:
            self._lexer.get_next()
            while self._lexer.lex == Lex.ident:
                self.parse_variable_declaration()
                self._check(Lex.semicollon)
        while self._lexer.lex == Lex.PROCEDURE:
            self.parse_procedure_declaration()
            self._check(Lex.semicollon)

    def _parse_const_declaration(self) -> Constant:
        identifier = self._parse_identdef()
        self._check(Lex.equal)
        value = self._parse_const_expression()


    def _parse_const_expression(self):
        self._parse_expression()

    def _parse_type_declaration(self):
        identifier = self._parse_identdef()
        self._check(Lex.equal)
        oberon_type = self._parse_type()
    
    def _parse_type(self):
        match self._lexer.lex:
            case Lex.Ident:
                composite_ident = self._parse_qualident()
            case Lex.ARRAY:
                array_type = self._parse_array_type()
            case Lex.RECORD:
                record_type = self._parse_record_type()
            case Lex.POINTER:
                pointer_type = self._parse_pointer_type()
            case Lex.PROCEDURE:
                procedure_type = self._parse_procedure_type()
            case _:
                self._raise_expected_exception("тип")
    
    def _calculate_array_type(self, array_sizes: list[int], element_type: OberonType) -> ArrayType:
        if len(array_sizes) == 1:
            return ArrayType(element_type, array_sizes[0])
        return ArrayType(self._calculate_array_type(array_sizes[1:], element_type), array_sizes[0])

    def _parse_array_type(self) -> ArrayType:
        self._check(Lex.ARRAY)
        array_lengths = []
        array_lengths.append(self._parse_length())
        while self._lexer.lex == Lex.comma:
            self._lexer.get_next()
            array_lengths.append(self._parse_length())
        self._check(Lex.OF)
        array_element_type = self._parse_type()
        return self._calculate_array_type(array_lengths, array_element_type)

    def _parse_length(self) -> int:
        return self._parse_const_expression()
    
    #Todo
