from lexer import *
from emmiter import *

class ParserError(Exception):

    position: int
    message: str

    def __init__(self, message: str, position: int):
        super().__init__(message)
        self.position = position
        self.message = message


class Parser:

    lexer: Lexer
    emitter: Emitter
    cur_token: Token
    peek_token: Token
    symbols: set
    labels_declared: set
    labels_gotoed: set

    def __init__(self, lexer: Lexer, emitter: Emitter):
        self.lexer = lexer
        self.emitter = emitter

        self.cur_token = None
        self.peek_token = None

        self.symbols = set()
        self.labels_declared = set()
        self.labels_gotoed = set()

        self.advance()
        self.advance()
    
    # Production rules:

    # program ::= statement*
    def program(self):
        self.emitter.header_line("#include <stdio.h>")
        self.emitter.header_line("int main(void){")

        while self.check_cur(TokenType.NEWLINE):
            self.advance()

        while not self.check_cur(TokenType.EOF):
            self.statement()

        for label in self.labels_gotoed:
            if label not in self.labels_declared:
                self.abort("attemp to GOTO to an undeclared label: '" + label + "'")

        self.emitter.emit_line("return 0;")
        self.emitter.emit_line("}")

    # One of the following statements...
    def statement(self):
        if self.check_cur(TokenType.PRINT):
            self.advance()

            if self.check_cur(TokenType.STRING):
                self.emitter.emit_line('printf("' + self.cur_token.text + '\\n");')
                self.advance()
            else:
                self.emitter.emit('printf("%.2f\\n", (float)(')
                self.expression()
                self.emitter.emit_line('));')

        elif self.check_cur(TokenType.IF):
            self.advance()
            self.emitter.emit('if(')
            self.comparison()

            self.require(TokenType.THEN)
            self.nl()
            self.emitter.emit_line('){')

            while not self.check_cur(TokenType.ENDIF):
                self.statement()
            
            self.require(TokenType.ENDIF)
            self.emitter.emit_line('}')

        elif self.check_cur(TokenType.WHILE):
            self.advance()
            self.emitter.emit('while(')
            self.comparison()

            self.require(TokenType.REPEAT)
            self.nl()
            self.emitter.emit_line('){')

            while not self.check_cur(TokenType.ENDWHILE):
                self.statement()
            
            self.require(TokenType.ENDWHILE)
            self.emitter.emit_line('}')

        elif self.check_cur(TokenType.LABEL):
            self.advance()

            if self.cur_token.text in self.labels_declared:
                self.abort("label already exists: '" + self.cur_token.text + "'")
            
            self.labels_declared.add(self.cur_token.text)

            self.emitter.emit_line(self.cur_token.text + ':')
            self.require(TokenType.IDENT)

        elif self.check_cur(TokenType.GOTO):
            self.advance()
            self.labels_gotoed.add(self.cur_token.text)
            self.emitter.emit_line("goto " + self.cur_token.text + ";")
            self.require(TokenType.IDENT)

        elif self.check_cur(TokenType.LET):
            self.advance()

            if self.cur_token.text not in self.symbols:
                self.symbols.add(self.cur_token.text)
                self.emitter.header_line("float " + self.cur_token.text + ";")

            self.emitter.emit(self.cur_token.text + " = ")
            self.require(TokenType.IDENT)
            self.require(TokenType.EQ)
            
            self.expression()
            self.emitter.emit_line(";")

        elif self.check_cur(TokenType.INPUT):
            self.advance()

            if self.cur_token.text not in self.symbols:
                self.symbols.add(self.cur_token.text)
                self.emitter.header_line("float " + self.cur_token.text + ";")

            self.emitter.emit_line('if(0 == scanf("%f", &' + self.cur_token.text + ")){")
            self.emitter.emit_line(self.cur_token.text + " = 0;")
            self.emitter.emit('scanf("%*s");')
            self.emitter.emit_line("}")
            self.require(TokenType.IDENT)

        else:
            self.abort('unexpected ' + self.cur_token.kind.name)
        
        self.nl()

    # nl ::= '\n'+
    def nl(self):
        self.require(TokenType.NEWLINE)
        while self.check_cur(TokenType.NEWLINE):
            self.advance()

    # comparison ::= expression ((...) expression)+
    def comparison(self):
        self.expression()

        if self.is_cur_tok_comparison():
            self.emitter.emit(self.cur_token.text)
            self.advance()
            self.expression()
        else:
            self.abort('expected comparison operator')
        
        while self.is_cur_tok_comparison():
            self.emitter.emit(self.cur_token.text)
            self.advance()
            self.expression()

    # Expressions' productions:
    
    def expression(self):
        self.term()

        while self.check_cur(TokenType.PLUS) or self.check_cur(TokenType.MINUS):
            self.emitter.emit(self.cur_token.text)
            self.advance()
            self.term()

    def term(self):
        self.unary()
        
        while self.check_cur(TokenType.ASTERISK) or self.check_cur(TokenType.SLASH):
            self.emitter.emit(self.cur_token.text)
            self.advance()
            self.unary()

    def unary(self):
        if self.check_cur(TokenType.PLUS) or self.check_cur(TokenType.MINUS):
            self.emitter.emit(self.cur_token.text)
            self.advance()
            self.unary()
        else:
            self.primary()

    def primary(self):
        if self.check_cur(TokenType.NUMBER):
            self.emitter.emit(self.cur_token.text)
            self.advance()
        elif self.check_cur(TokenType.IDENT):
            if self.cur_token.text not in self.symbols:
                self.abort("undefined reference to '" + self.cur_token.text + "'")
            
            self.emitter.emit(self.cur_token.text)
            self.advance()
        else:
            self.abort("unexpected token")

    # Helpers functions:

    # Checks if the current token is a comparison operator
    def is_cur_tok_comparison(self):
        return self.check_cur(TokenType.GT) \
            or self.check_cur(TokenType.GTEQ) \
            or self.check_cur(TokenType.LT) \
            or self.check_cur(TokenType.LTEQ) \
            or self.check_cur(TokenType.EQEQ) \
            or self.check_cur(TokenType.NOTEQ)

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
