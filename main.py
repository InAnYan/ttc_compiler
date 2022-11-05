from lexer import *

def main():
    input = "+-/ *"
    lexer = Lexer(input)
    result = []
    token = lexer.get_token()
    while token.kind != TokenType.EOF:
        print(token.kind)
        result.append(token)
        token = lexer.get_token()
    

if __name__ == '__main__':
    main()