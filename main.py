from lexer import *
from parser import *
import sys

def main():
    print("Teeny Tiny Compiler")

    if len(sys.argv) != 2:
        sys.exit("error: compiler needs source file as argument.")
    
    with open(sys.argv[1], 'r') as fin:
        input = fin.read()
    
    lexer = Lexer(input)
    parser = Parser(lexer)

    parser.program()
    print("Parsing completed.")


if __name__ == '__main__':
    main()