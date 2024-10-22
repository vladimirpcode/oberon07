from lexer import Lexer, Lex


class Parser:
    def __init__(self, program: str) -> None:
        self._lexer = Lexer(program)
        self._parse_module()

    def _raise_expected_exception(self, expected: str):
        raise Exception(f"Ожидалось {expected}, но {self._lexer.lex.value[0]}")

    def _check(self, lex: Lex):
        if self._lexer != lex:
            self._raise_expected_exception(lex.value[0], self._lexer.lex)
        self._lexer.get_next()

    def _parse_module(self):
        self._check(Lex.MODULE)
        if self._lexer.lex != Lex.ident:
            self._raise_expected_exception("имя модуля")
        module_name = self._lexer.value
        self._lexer.get_next()
        #ToDo

    