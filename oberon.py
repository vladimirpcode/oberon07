from syntax_analyzer import Parser
import os

def compile(program: str):
    parser = Parser(program)



def _compile_one_module(path_to_file: str):
    f = open(path_to_file)
    program = f.read()
    f.close()
    try:
        compile(program)
        print(f"{path_to_file}: успешно скомпилировано")
    except Exception as e:
        raise e
    

for file in os.listdir("code_samples"):
    _compile_one_module("code_samples" + "/" + file)