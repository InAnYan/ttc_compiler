import enum

class TokenType(enum.Enum):
    # Basic types.
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3

    # Keywords.
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111

    # Operators.
    EQ = 201  
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211


class Token:
    text: str
    kind: TokenType
    position: int

    def __init__(self, text: str, kind: TokenType, position: int):
        self.text = text
        self.kind = kind
        self.position = position


class LexerError(Exception):

    position: int
    message: str

    def __init__(self, message: str, position: int):
        super().__init__(message)
        self.position = position
        self.message = message


class Lexer:

    source: str
    cur_char: str
    cur_pos: int

    def __init__(self, input: str):
        self.source = input + '\n'
        self.cur_char = ''
        self.cur_pos = -1

        self.next_char()

    # Processes the next character.
    def next_char(self):
        self.cur_pos += 1
        if self.cur_pos >= len(self.source):
            self.cur_char = '\0'
        else:
            self.cur_char = self.source[self.cur_pos]

    # Return the lookahead character.
    def peek(self):
        if self.cur_pos + 1 >= len(self.source):
            return '\0'
        else:
            return self.source[self.cur_pos + 1]

    # If cur_char == char, then it does next_char
    # and returns true, else return false
    def match(self, char: str) -> bool:
        if self.cur_char == char:
            self.next_char()
            return True
        else:
            return False

    # Ends lexer execution.
    def abort(self, message: str):
        raise LexerError(message, self.cur_pos)

    # Skips whitespace except newlines.
    def skip_whitespace(self):
        while self.cur_char == ' ' or self.cur_char == '\t' or self.cur_char == '\r':
            self.next_char()

    # Skips comments in the code.
    def skip_comment(self):
        if self.match('#'):
            while self.cur_char != '\n':
                self.next_char()

    # Return the previous character.
    def previous(self) -> str:
        if self.cur_pos >= 1 and self.cur_pos < len(self.source):
            return self.source[self.cur_pos - 1]
        else:
            return '\0'

    # Creates a token based on previous character.
    def char_token(self, kind: TokenType) -> Token:
        # TODO: Test pos
        return Token(self.previous(), kind, self.cur_pos - 1)

    # Parses a string.
    def string(self) -> Token:
        start_pos = self.cur_pos
            
        while self.cur_char != '"':
            if self.cur_char == '\r' or self.cur_char == '\n' \
            or self.cur_char == '\t' or self.cur_char == '\\' \
            or self.cur_char == '%':
                self.abort("illegal character in string: '" + self.cur_char + "'")
                
            self.next_char()
            
        self.next_char()

        token_text = self.source[start_pos: self.cur_pos - 1]
        # TODO: Test start_pos
        return Token(token_text, TokenType.STRING, start_pos - 1)

    # Parses a number. 
    # First digit should not be consumed.
    def number(self) -> Token:
        start_pos = self.cur_pos

        while self.peek().isdigit():
            self.next_char()
        
        if self.peek() == '.':
            self.next_char()

            if not self.peek().isdigit():
                self.abort("expected a digit after '.'")
            
            while self.peek().isdigit():
                self.next_char()

        self.next_char()

        token_text = self.source[start_pos : self.cur_pos]
        # TODO: Test start_pos
        return Token(token_text, TokenType.NUMBER, start_pos)

    # Parses an identifier.
    # First digit should not be consumed.
    def identifier(self) -> Token:
        start_pos = self.cur_pos

        while self.peek().isalnum():
            self.next_char()

        self.next_char()

        token_text = self.source[start_pos : self.cur_pos]
        # TODO: Test start_pos
        return Token(token_text, self.check_if_keyword(token_text), start_pos)

    # Checks if a string is a keyword, returns the corresponding token type.
    def check_if_keyword(self, txt: str):
        # Uses a trick.
        for kind in TokenType:
            if kind.name == txt and kind.value >= 100 and kind.value < 200:
                return kind
        return TokenType.IDENT

    # Returns the next token.
    def get_token(self) -> Token:
        self.skip_whitespace()
        self.skip_comment()

        if self.match('+'):
            return self.char_token(TokenType.PLUS)
        elif self.match('-'):
            return self.char_token(TokenType.MINUS)
        elif self.match('*'):
            return self.char_token(TokenType.ASTERISK)
        elif self.match('/'):
            return self.char_token(TokenType.SLASH)
        elif self.match('\n'):
            return self.char_token(TokenType.NEWLINE)
        elif self.match('\0'):
            return self.char_token(TokenType.EOF)
        elif self.match('='):
            if self.match('='):
                return Token('==', TokenType.EQEQ)
            else:
                return self.char_token(TokenType.EQ)
        elif self.match('>'):
            if self.match('='):
                return Token('>=', TokenType.GTEQ)
            else:
                return self.char_token(TokenType.GT)
        elif self.match('<'):
            if self.match('='):
                return Token('<=', TokenType.LTEQ)
            else:
                return self.char_token(TokenType.LT)
        elif self.match('!'):
            if self.match('='):
                return Token('!=', TokenType.NOTEQ)
            else:
                self.abort("expected '!=', got '!'")
        elif self.match('"'):
            return self.string()
        elif self.cur_char.isdigit():
            return self.number()        
        elif self.cur_char.isalpha():
            return self.identifier()    
        else:
            self.abort("unknown character: '" + self.cur_char + "'")
