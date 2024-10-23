from syntax_analyzer import Parser

def compile(program: str):
    parser = Parser(program)



f = open("code_samples/main.oberon07")
program = f.read()
f.close()
compile(program)