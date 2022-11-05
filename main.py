from lexer import *
from parser import *
from emmiter import *
import sys

def main():
    print("Teeny Tiny Compiler")

    if len(sys.argv) != 2:
        sys.exit("error: compiler needs source file as argument.")
    
    with open(sys.argv[1], 'r') as fin:
        input = fin.read()
    
    try:
        lexer = Lexer(input)
        emitter = Emitter("out.c" if len(sys.argv) < 3 else sys.argv[2])
        parser = Parser(lexer, emitter)

        parser.program()
        emitter.write_file()
        print("Compiling completed.")
    except LexerError as e:
        report_error(e.message, e.position)
    except ParserError as e:
        report_error(e.message, e.position)


def report_error(message: str, position: int):
    print(sys.argv[1] + ':' + str(position) + ': error: ' + message)


if __name__ == '__main__':
    main()