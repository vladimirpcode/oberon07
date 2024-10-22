from lexer import *

def compile(program: str):
    lexer = Lexer(program)
    counter = 0
    while lexer.lex != Lex.end_of_text:
        print(lexer.lex.value[0])
        lexer.get_next()
        counter += 1



f = open("code_samples/main.oberon07")
program = f.read()
f.close()
compile(program)