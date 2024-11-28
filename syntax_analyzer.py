from lexer import Lexer, Lex
from oberon_types import *
from ast_node import AstNode
from nametable import *


class Parser:
    def __init__(self, program: str) -> None:
        self._lexer = Lexer(program)
        self._module_name = None
        self._nametable = Nametable()
        ### DEBUG
        self._nametable.add_entry(NameTableEntry(CompositeIdentifier("Log", "String"), Procedure()))
        self._nametable.add_entry(NameTableEntry(CompositeIdentifier("Log", "Clear"), Procedure()))
        self._nametable.add_entry(NameTableEntry(CompositeIdentifier("Log", "Ln"), Procedure()))
        self._nametable.add_entry(NameTableEntry(CompositeIdentifier("INTEGER", None), BasicType(None, Identifier("INTEGER", False))))
        self._nametable.add_entry(NameTableEntry(CompositeIdentifier("REAL", None), BasicType(None, Identifier("REAL", False))))
        self._nametable.add_entry(NameTableEntry(CompositeIdentifier("BOOLEAN", None), BasicType(None, Identifier("BOOLEAN", False))))
        self._nametable.add_entry(NameTableEntry(CompositeIdentifier("ASSERT", None),  Procedure()))
        ### NO_DEBUG
        self._parse_module()

    def _raise_expected_exception(self, expected: str):
        raise Exception(f"{self._lexer.get_context()}\nОжидалось {expected}, но {self._lexer.lex.value[0]}")

    def resolve_type(self, typename: Identifier | CompositeIdentifier) -> OberonType:
        nametable_entries = self._nametable.get_all_identifiers_for_current_scope()
        for entry in nametable_entries:
            if not issubclass(type(entry.entity), OberonType):
                continue
            if entry.name == typename:
                return entry.entity
        raise Exception(f"неизвестные тип {identifier_to_str(typename)}")

    def _check(self, lex: Lex):
        if self._lexer.lex != lex:
            self._raise_expected_exception(lex.value[0])
        self._lexer.get_next()

    def _parse_ident(self) -> str:
        if self._lexer.lex != Lex.ident:
            self._raise_expected_exception("идентификатор")
        name = self._lexer.value
        self._lexer.get_next()
        return name
    
    def _parse_qualident(self) -> CompositeIdentifier:
        parent_name = self._parse_ident()
        child_name = None
        if self._lexer.lex == Lex.dot:
            self._lexer.get_next()
            child_name = self._parse_ident()
        return CompositeIdentifier(parent_name, child_name)

    def _parse_identdef(self) -> Identifier:
        ident = self._parse_ident()
        is_exported = False
        if self._lexer.lex == Lex.multiple:
            self._lexer.get_next()
            is_exported = True
        return Identifier(ident, is_exported)
    
    def _parse_number(self) -> float | int:
        if self._lexer.lex != Lex.number:
            self._raise_expected_exception("число")
        number = self._lexer.value
        self._lexer.get_next()
        return number
    
    def _parse_sring(self) -> str:
        if self._lexer.lex != Lex.string:
            self._raise_expected_exception("строка")
        s = self._lexer.value
        self._lexer.get_next()
        return s

    def _parse_const_declaration(self) -> Constant:
        const_identifier = self._parse_identdef()
        self._check(Lex.equal)
        value = self._parse_const_expression()
        const_type: OberonType = None
        if isinstance(value, int):
            const_type = self.resolve_type("INTEGER")
        elif isinstance(value, float):
                const_type = self.resolve_type("REAL")
        elif isinstance(value, str):
            if len(str) == 1:
                const_type = self.resolve_type("CHAR")
            else:
                const_type = self.resolve_type("STRING")
        self._nametable.add_entry(NameTableEntry(const_identifier, Constant(const_identifier.name, value, const_type)))


    def _parse_const_expression(self):
        self._parse_expression()

    ######################################################
    #                  TYPE DECLARATIONS RULES           #
    ######################################################

    def _parse_type_declaration(self):
        identifier = self._parse_identdef()
        self._check(Lex.equal)
        oberon_type = self._parse_type()
    
    def _parse_type(self) -> OberonType:
        match self._lexer.lex:
            case Lex.ident:
                composite_ident = self._parse_qualident()
                #ToDo resolve_type
            case Lex.ARRAY:
                array_type = self._parse_array_type()
                return array_type
            case Lex.RECORD:
                record_type = self._parse_record_type()
                return record_type
            case Lex.POINTER:
                pointer_type = self._parse_pointer_type()
                return pointer_type
            case Lex.PROCEDURE:
                procedure_type = self._parse_procedure_type()
                return procedure_type
            case _:
                self._raise_expected_exception("тип")
    
    def _calculate_array_type(self, array_sizes: list[int], element_type: OberonType) -> ArrayType:
        if len(array_sizes) == 1:
            return ArrayType(self._module_name, None, element_type, array_sizes[0])
        return ArrayType(self._module_name, None, self._calculate_array_type(array_sizes[1:], element_type), array_sizes[0])

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
    
    def _parse_record_type(self) -> RecordType:
        self._check(Lex.RECORD)
        base_type = None
        if self._lexer.lex == Lex.left_bracket:
            self._lexer.get_next()
            base_type = self._parse_base_type()
            self._check(Lex.right_bracket)
        record_fields = []
        if self._lexer.lex == Lex.ident:
            record_fields = self._parse_field_list_sequence()
        self._check(Lex.END)
        return RecordType(None, None, base_type, record_fields)

    def _parse_base_type(self) -> OberonType:
        composite_identifier = self._parse_qualident()
        # Todo: type resolve

    def _parse_field_list_sequence(self) -> list[RecordField]:
        all_record_fields = []
        all_record_fields += self._parse_field_list()
        while self._lexer.lex == Lex.semicollon:
            self._lexer.get_next()
            all_record_fields += self._parse_field_list()
        return all_record_fields

    def _parse_field_list(self) -> list[RecordField]:
        identifiers = self._parse_ident_list()
        self._check(Lex.colon)
        fields_type = self._parse_type()
        return [RecordField(ident, fields_type) for ident in identifiers]
        
    def _parse_ident_list(self) -> list[Identifier]:
        identifiers = []
        identifiers.append(self._parse_identdef())
        while self._lexer.lex == Lex.comma:
            self._lexer.get_next()
            identifiers.append(self._parse_identdef())
        return identifiers
    
    def _parse_pointer_type(self) -> PointerType:
        self._check(Lex.POINTER)
        self._check(Lex.TO)
        return PointerType(self._parse_type)

    def _parse_procedure_type(self) -> ProcedureType:
        self._check(Lex.PROCEDURE)
        if self._lexer.lex == Lex.left_bracket:
            return self._parse_formal_parameters()
        return ProcedureType(self._module_name, None, NoReturnType, list())
    
    ######################################################
    #                  TYPE DECLARATIONS RULES END       #
    ######################################################

    def _parse_variable_declaration(self):
        identifiers = self._parse_ident_list()
        self._check(Lex.colon)
        variables_type = self._parse_type()
        for name in identifiers:
            self._nametable.add_entry(NameTableEntry(name, Variable(identifier_to_str(name), variables_type)))

    ######################################################
    #                  EXPRESSION RULES                  #
    ######################################################

    def _parse_expression(self) -> AstNode:
        self._parse_simple_expression()
        if self._lexer.lex in [Lex.equal, Lex.hash, Lex.less,
                               Lex.less_equal, Lex.greater,
                               Lex.greater_equal, Lex.IN, Lex.IS]:
            self._lexer.get_next()
            self._parse_simple_expression()
    
    def _parse_simple_expression(self) -> AstNode:
        if self._lexer.lex in [Lex.plus, Lex.minus]:
            self._lexer.get_next()
        self._parse_term()
        while self._lexer.lex in [Lex.plus, Lex.minus, Lex.OR]:
            self._lexer.get_next()
            self._parse_term()

    def _parse_term(self) -> AstNode:
        self._parse_factor()
        while self._lexer.lex in [Lex.multiple, Lex.divide, Lex.DIV, 
                                  Lex.MOD, Lex.ampersand]:
            self._lexer.get_next()
            self._parse_factor()
    
    def _parse_factor(self) -> AstNode:
        if self._lexer.lex in [Lex.number, Lex.string, Lex.NIL, Lex.TRUE,
                               Lex.FALSE]:
            self._lexer.get_next()
        elif self._lexer.lex == Lex.left_curly_bracket:
            self._parse_set()
        elif self._lexer.lex == Lex.ident:
            self._parse_designator()
            if self._lexer.lex == Lex.left_bracket:
                self._parse_actual_parameters()
        elif self._lexer.lex == Lex.left_bracket:
            self._lexer.get_next()
            self._parse_expression()
            self._check(Lex.right_bracket)
        elif self._lexer.lex == Lex.tilde:
            self._lexer.get_next()
            self._parse_factor()
        else:
            self._raise_expected_exception("число, строка, NIL, TRUE, FALSE, множество, вызов процедуры, переменная, (выражение), ~")
    
    def _is_procedure(self, composite_identifier: CompositeIdentifier) -> bool:
        ident_str = identifier_to_str(composite_identifier)
        nametable_entries = self._nametable.get_all_identifiers_for_current_scope()
        for entry in nametable_entries:
            if ident_str == identifier_to_str(entry.name):
                if isinstance(entry.entity, Procedure):
                    return True
                else:
                    return False
        raise Exception("неизвестный идентификатор " + ident_str)

    def _parse_designator(self):
        composite_identifier = self._parse_qualident()
        if self._is_procedure(composite_identifier):
            return
        while self._lexer.lex in [Lex.dot, Lex.left_square_bracket, Lex.caret, Lex.left_bracket]:
            self._parse_selector()
    
    def _parse_selector(self):
        match self._lexer.lex:
            case Lex.dot:
                self._lexer.get_next()
                self._parse_ident()
            case Lex.left_square_bracket:
                self._lexer.get_next()
                self._parse_exp_list()
                self._check(Lex.right_square_bracket)
            case Lex.caret:
                self._lexer.get_next()
            case Lex.left_bracket:
                self._lexer.get_next()
                self._parse_qualident()
                self._check(Lex.right_bracket)
            case _:
                self._raise_expected_exception(".идентификатор, [список выражений], ^, (составной идентификатор)")
    
    def _parse_set(self):
        self._check(Lex.left_curly_bracket)
        if self._lexer.lex != Lex.right_curly_bracket:
            self._parse_element()
            while self._lexer.lex == Lex.comma:
                self._lexer.get_next()
                self._parse_element()
        self._check(Lex.right_curly_bracket)

    def _parse_element(self):
        self._parse_expression()
        if self._lexer.lex == Lex.double_dot:
            self._lexer.get_next()
            self._parse_expression()

    def _parse_exp_list(self):
        self._parse_expression()
        while self._lexer.lex == Lex.comma:
            self._lexer.get_next()
            self._parse_expression()

    def _parse_actual_parameters(self):
        self._check(Lex.left_bracket)
        if self._lexer.lex != Lex.right_bracket:
            self._parse_exp_list()
        self._check(Lex.right_bracket)

    ######################################################
    #                  EXPRESSION RULES END              #
    ######################################################

    ######################################################
    #                  STATEMENT RULES                   #
    ######################################################

    def _parse_statement(self):
        match self._lexer.lex:
            case Lex.ident:
                self._parse_designator()
                if self._lexer.lex == Lex.assignment:
                    self._lexer.get_next()
                    self._parse_expression()
                else:
                    if self._lexer.lex == Lex.left_bracket:
                        self._parse_actual_parameters()
            case Lex.IF:
                self._parse_if_statement()
            case Lex.CASE:
                self._parse_case_statement()
            case Lex.WHILE:
                self._parse_while_statement()
            case Lex.REPEAT:
                self._parse_repeat_statement()
            case Lex.FOR:
                self._parse_for_statement()
            case _:
                self._raise_expected_exception("оператор")

    def _parse_statement_sequence(self):
        self._parse_statement()
        while self._lexer.lex == Lex.semicollon:
            self._lexer.get_next()
            self._parse_statement()

    def _parse_if_statement(self):
        self._check(Lex.IF)
        self._parse_expression()
        self._check(Lex.THEN)
        self._parse_statement_sequence()
        while self._lexer.lex == Lex.ELSIF:
            self._lexer.get_next()
            self._parse_expression()
            self._check(Lex.THEN)
            self._parse_statement_sequence
        if self._lexer.lex == Lex.ELSE:
            self._lexer.get_next()
            self._parse_statement_sequence()
        self._check(Lex.END)

    def _parse_case_statement(self):
        self._check(Lex.CASE)
        self._parse_expression()
        self._check(Lex.OF)
        self._parse_case()
        while self._lexer.lex == Lex.vertical_line:
            self._lexer.get_next()
            self._parse_case()
        self._check(Lex.END)
    
    def _parse_case(self):
        if self._lexer.lex in [Lex.string, Lex.ident] or (self._lexer.lex == Lex.number and type(self._lexer.value) is int):
            self._parse_case_label_list()
            self._check(Lex.colon)
            self._parse_statement_sequence()
        
    def _parse_case_label_list(self):
        self._parse_label_range()
        while self._lexer.lex == Lex.comma:
            self._lexer.get_next()
            self._parse_label_range()
    
    def _parse_label_range(self):
        self._parse_label()
        if self._lexer.lex == Lex.double_dot:
            self._lexer.get_next()
            self._parse_label()
    
    def _parse_label(self):
        if self._lexer.lex == Lex.number and type(self._lexer.value) is int:
            self._lexer.get_next()
        elif self._lexer.lex == Lex.string:
            self._lexer.get_next()
        elif self._lexer.lex == Lex.ident:
            self._parse_qualident()
        else:
            self._raise_expected_exception("метка case")

    def _parse_while_statement(self):
        self._check(Lex.WHILE)
        self._parse_expression()
        self._check(Lex.DO)
        self._parse_statement_sequence()
        while self._lexer.lex == Lex.ELSIF:
            self._lexer.get_next()
            self._parse_expression()
            self._check(Lex.DO)
            self._parse_statement_sequence()
        self._check(Lex.END)

    def _parse_repeat_statement(self):
        self._check(Lex.REPEAT)
        self._parse_statement_sequence()
        self._check(Lex.UNTIL)
        self._parse_expression()

    def _parse_for_statement(self):
        self._check(Lex.FOR)
        self._parse_ident()
        self._check(Lex.assignment)
        self._parse_expression()
        self._check(Lex.TO)
        self._parse_expression()
        if self._lexer.lex == Lex.BY:
            self._lexer.get_next()
            self._parse_const_expression()


    ######################################################
    #                  STATEMENT RULES END               #
    ######################################################

    ######################################################
    #              OTHER DECLARATIONS RULES              #
    ######################################################
    
    def _parse_procedure_declaration(self) -> Procedure:
        procedure = Procedure()
        procedure.head = self._parse_procedure_heading()
        self._nametable.add_entry(NameTableEntry(procedure.head.name, procedure))
        self._nametable.open_scope()
        self._add_proc_params_to_nametable(procedure.head.procedure_type.parameters)
        self._check(Lex.semicollon)
        procedure.body = self._parse_procedure_body()
        self._parse_ident()
        self._nametable.close_scope()
        return procedure

    def _parse_procedure_heading(self) -> ProcedureHead:
        procedure_head = ProcedureHead(ProcedureType(self._module_name, None, NoReturnType, list()), None)
        self._check(Lex.PROCEDURE)
        procedure_head.name = self._parse_identdef()
        if self._lexer.lex == Lex.left_bracket:
            procedure_head.procedure_type = self._parse_formal_parameters()
        return procedure_head
    
    def _parse_procedure_body(self) -> ProcedureBody:
        self._parse_declaration_sequence()
        if self._lexer.lex == Lex.BEGIN:
            self._lexer.get_next()
            self._parse_statement_sequence()
            if self._lexer.lex == Lex.RETURN:
                self._lexer.get_next()
                self._parse_expression()
            self._check(Lex.END)

    def _parse_declaration_sequence(self):
        if self._lexer.lex == Lex.CONST:
            self._lexer.get_next()
            while self._lexer.lex == Lex.ident:
                self._parse_const_declaration()
                self._check(Lex.semicollon)
        if self._lexer.lex == Lex.TYPE:
            self._lexer.get_next()
            while self._lexer.lex == Lex.ident:
                self._parse_type_declaration()
                self._check(Lex.semicollon)
        if self._lexer.lex == Lex.VAR:
            self._lexer.get_next()
            while self._lexer.lex == Lex.ident:
                self._parse_variable_declaration()
                self._check(Lex.semicollon)
        while self._lexer.lex == Lex.PROCEDURE:
            self._parse_procedure_declaration()
            self._check(Lex.semicollon)

    def _add_proc_params_to_nametable(self, procedure_parameters: list[ProcedureParameter]):
        for param in procedure_parameters:
            self._nametable.add_entry(NameTableEntry(Identifier(param.name, False), param))

    def _parse_formal_parameters(self) -> ProcedureType:
        self._check(Lex.left_bracket)
        procedure_parameters: list[ProcedureParameter] = list()
        if self._lexer.lex != Lex.right_bracket:
            procedure_parameters += self._parse_fp_section()
            while self._lexer.lex == Lex.semicollon:
                self._lexer.get_next()
                procedure_parameters += self._parse_fp_section()
        self._check(Lex.right_bracket)
        return_type = NoReturnType(None, None)
        if self._lexer.lex == Lex.colon:
            self._lexer.get_next()
            return_type = self.resolve_type(self._parse_qualident())
        return ProcedureType(self._module_name, None, return_type, procedure_parameters)

    def _parse_fp_section(self) -> list[ProcedureParameter]:
        by_reference = False
        if self._lexer.lex == Lex.VAR:
            by_reference = True
            self._lexer.get_next()
        parameter_names: list[str] = list()
        parameter_names.append(self._parse_ident())
        while self._lexer.lex == Lex.comma:
            self._lexer.get_next()
            parameter_names.append(self._parse_ident())
        self._check(Lex.colon)
        parameters_type = self._parse_formal_type()
        procedure_parameters: list[ProcedureParameter] = list()
        for name in parameter_names:
            procedure_parameters.append(ProcedureParameter(name, parameters_type, by_reference))
        return procedure_parameters


    def _parse_formal_type(self) -> OberonType:
        formal_type: OberonType = None
        if self._lexer.lex == Lex.ARRAY:
            formal_type = self._parse_array_type()
        name = self._parse_qualident()
        if isinstance(formal_type, ArrayType):
            formal_type.element_type = self.resolve_type(name)
        else:
            formal_type = self.resolve_type(name)
        return formal_type

    ######################################################
    #              OTHER DECLARATIONS RULES END          #
    ######################################################

    def _parse_module(self):
        self._check(Lex.MODULE)
        self._module_name = self._parse_ident()
        self._check(Lex.semicollon)
        if self._lexer.lex == Lex.IMPORT:
            self._parse_import_list()
        self._parse_declaration_sequence()
        if self._lexer.lex == Lex.BEGIN:
            self._lexer.get_next()
            self._parse_statement_sequence()
        self._check(Lex.END)
        if self._parse_ident() != self._module_name:
            self._raise_expected_exception(f"имя модуля {self._module_name}")
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
            alias = imported_module_name
            imported_module_name = self._lexer.value
            self._lexer.get_next()
