from enum import Enum, auto, unique

class WrapperForReceivingCharacters:
    EOT = chr(4)

    def __init__(self, s: str) -> None:
        self._data = s
        self.ch = ''
        self._index = 0
        self.get_next()
    
    def get_next(self):
        if self._index >= len(self._data):
            self.ch = self.EOT
            return
        self.ch = self._data[self._index]
        self._index += 1

    def is_ch_hex_digit(self) -> bool:
        return self.ch in ['A', 'B', 'C', 'D', 'E', 'F']
    

# значения используются и для определения ключевых слов
# и для вывода на печать, поэтому где не ключ. слово, там 
# словесное значение обрамлено подчеркиваниями
@unique
class Lex(Enum):
    ident = "_идентификатор_",
    number = "_число_",
    string = "_строка_",
    plus = "+",                  # +
    minus = "-",                 # +
    multiple = "*",              # *
    divide = "/",                # /
    tilde = "~",                 # ~
    ampersand = "&",             # &
    dot = ".",                   # .
    comma = ",",                 # ,
    semicollon = ";",            # ;
    vertical_line = "|",         # |
    left_bracket = "(",          # (
    right_bracket = ")",         # )
    left_square_bracket = "[",   # [
    right_square_bracket = "]",  # ]
    left_curly_bracket = "{",    # {
    right_curly_bracket = "}",   # }
    assignment = ":=",           # :=
    caret = "^",                 # ^ 
    equal = "=",                 # =
    hash = "#",                  # #
    less = "<",                  # <
    greater = ">",               # >
    less_equal = "<=",           # <=
    greater_equal = ">=",        # >=
    double_dot = "..",           # ..
    colon = ":",                 # :
    ARRAY = "ARRAY",
    BEGIN = "BEGIN",
    BY = "BY",
    CASE = "CASE",
    CONST = "CONST",
    DIV = "DIV",
    DO = "DO",
    ELSE = "ELSE",
    ELSIF = "ELSIF",
    END = "END",
    FALSE = "FALSE",
    FOR = "FOR",
    IF = "IF",
    IMPORT = "IMPORT",
    IN = "IN",
    IS = "IS",
    MOD = "MOD",
    MODULE = "MODULE",
    NIL = "NIL",
    OF = "OF",
    OR = "OR",
    POINTER = "POINTER",
    PROCEDURE = "PROCEDURE",
    RECORD = "RECORD",
    REPEAT = "REPEAT",
    RETURN = "RETURN",
    THEN = "THEN",
    TO = "TO",
    TRUE = "TRUE",
    TYPE = "TYPE",
    UNTIL = "UNTIL",
    VAR = "VAR",
    WHILE = "WHILE",
    unknown_lex = "_неизвестная лексема_",
    end_of_text = "_конец текста_"




class Lexer:
    def __init__(self, s: str) -> None:
        self._wrap = WrapperForReceivingCharacters(s)
        self.value = ""
        self.lex = Lex.unknown_lex
        self.get_next()

    def get_next(self):
        while self._wrap.ch.isspace():
            self._wrap.get_next()
        if self._wrap.ch == self._wrap.EOT:
            self.lex = Lex.end_of_text
        elif self._wrap.ch.isnumeric():
            number_str = self._wrap.ch
            self.get_next()
            while self._wrap.isnumeric() or self._wrap.is_ch_hex_digit:
                number_str += self._wrap.ch
                self.get_next()
            if self._wrap.ch == 'H':
                self._wrap.get_next()
                self.lex = Lex.number
                self.value = int(number_str, base=16)
            elif self._wrap == 'X':
                self._wrap.get_next()
                self.lex = Lex.string
                self.value = chr(int(number_str, base=16))
            elif self._wrap == '.':
                number_str += self._wrap
                self._wrap.get_next()
                while self._wrap.ch.isnumeric():
                    number_str += self._wrap.ch
                    self._wrap.get_next()
                if self._wrap.ch == "E":
                    number_str += self._wrap.ch
                    self._wrap.get_next()
                    if self._wrap.ch in ['+', '-']:
                        number_str += self._wrap.ch
                        self._wrap.get_next()
                    while self._wrap.ch.isnumeric():
                        number_str += self._wrap.ch
                        self._wrap.get_next()
                self.lex = Lex.number
                value = float(number_str)
                        
            else:
                self.lex = Lex.number
                self.value = int(number_str, base=10)
        elif self._wrap.ch.isalpha():
            ident = self._wrap.ch
            self._wrap.get_next()
            while self._wrap.ch.isalpha() or self._wrap.ch.isnumeric():
                ident += self._wrap.ch
                self._wrap.get_next()
            self.lex = Lex.ident
            self.value = ident
            for lex in Lex.__members__.values():
                if lex.value[0] == ident:
                    self.lex = lex
                    break
        elif self._wrap.ch == '"':
            self._wrap.get_next()
            string = ""
            while self._wrap.ch not in ['"', self._wrap.EOT]:
                string += self._wrap.ch
                self._wrap.get_next()
            if self._wrap.ch == '"':
                self.lex = Lex.string
                self._wrap.get_next()
            else:
                self.lex = Lex.end_of_text
        else:
            self.lex = Lex.unknown_lex
            for lex in Lex.__members__.values():
                if lex.value[0] == self._wrap.ch:
                    self.lex = lex
                    self._wrap.get_next()
                    break
            if self.lex == Lex.dot:
                if self._wrap.ch == '.':
                    self.lex = Lex.double_dot
                    self._wrap.get_next()
            elif self.lex == Lex.less:
                if self._wrap.ch == '=':
                    self.lex = Lex.less_equal
                    self._wrap.get_next()
            elif self.lex == Lex.greater:
                if self._wrap.ch == '=':
                    self.lex = Lex.greater_equal
                    self._wrap.get_next()
            elif self.lex == Lex.colon:
                if self._wrap.ch == '=':
                    self.lex = Lex.assignment
                    self._wrap.get_next()

                
            
