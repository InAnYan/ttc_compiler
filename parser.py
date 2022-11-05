from lexer import *

class ParserError(Exception):

    position: int
    message: str

    def __init__(self, message: str, position: int):
        super().__init__(message)
        self.position = position
        self.message = message


class Parser:

    lexer: Lexer
    cur_token: Token
    peek_token: Token

    def __init__(self, lexer: Lexer):
        self.lexer = lexer

        self.cur_token = None
        self.peek_token = None

        self.advance()
        self.advance()
    
    # Production rules:

    # program ::= statement*
    def program(self):
        print("PROGRAM")

        while not self.check_cur(TokenType.EOF):
            self.statement()

    # One of the following statements...
    def statement(self):
        if self.check_cur(TokenType.PRINT):
            print('STATEMENT-PRINT')
            self.advance()

            if self.check_cur(TokenType.STRING):
                self.advance()
            else:
                self.expression()
        elif self.check_cur(TokenType.IF):
            print('STATEMENT-IF')
            self.advance()
            self.comparison()

            self.require(TokenType.THEN)
            self.nl()

            while not self.check_cur(TokenType.ENDIF):
                self.statement()
            
            self.require(TokenType.ENDIF)
        elif self.check_cur(TokenType.WHILE):
            print('STATEMENT-WHILE')
            self.advance()
            self.comparison()

            self.require(TokenType.REPEAT)
            self.nl()

            while not self.check_cur(TokenType.ENDWHILE):
                self.statement()
            
            self.require(TokenType.ENDWHILE)
        elif self.check_cur(TokenType.LABEL):
            print('STATEMENT-LABEL')
            self.advance()
            self.require(TokenType.IDENT)
        elif self.check_cur(TokenType.GOTO):
            print('STATEMENT-GOTO')
            self.advance()
            self.require(TokenType.IDENT)
        elif self.check_cur(TokenType.LET):
            print('STATEMENT-LET')
            self.advance()
            self.require(TokenType.IDENT)
            self.require(TokenType.EQ)
            self.expression()
        elif self.check_cur(TokenType.INPUT):
            print('STATEMENT-INPUT')
            self.advance()
            self.require(TokenType.INPUT)
        else:
            self.abort('unexpected ' + self.cur_token.kind.name)
        
        self.nl()

    # nl ::= '\n'+
    def nl(self):
        print('NEWLINE')
        self.require(TokenType.NEWLINE)
        while self.check_cur(TokenType.NEWLINE):
            self.advance()

    # Helpers functions:

    # Ends parser execution.
    def abort(self, message):
        raise ParserError(message, self.cur_token.position)

    # Tries to match current token. If not, then aborts. Advances.
    def require(self, kind: TokenType):
        if not self.match(kind):
            self.abort('expected ' + kind.name + ', got ' + self.cur_token.kind.name)

    def match(self, kind: TokenType) -> bool:
        if self.check_cur(kind):
            self.advance()
            return True
        else:
            return False

    # Returns true if the current token matches.
    def check_cur(self, kind: TokenType) -> bool:
        return self.cur_token.kind == kind

    # Returns true if the next token matches.
    def check_peek(self, kind: TokenType) -> bool:
        return self.peek_token.kind == kind

    # Advances the current token.
    def advance(self):
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.get_token()
