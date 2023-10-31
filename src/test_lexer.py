import unittest
from lexer import *


class TestLexer(unittest.TestCase):
    
    def process_input(self, input):
        lexer = Lexer(input)
        result = []
        token = lexer.get_token()
        while token.kind != TokenType.EOF:
            result.append(token)
            token = lexer.get_token()
        return result

    def test_basic(self):
        result = self.process_input('+- /*')
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0].kind, TokenType.PLUS)
        self.assertEqual(result[1].kind, TokenType.MINUS)
        self.assertEqual(result[2].kind, TokenType.SLASH)
        self.assertEqual(result[3].kind, TokenType.ASTERISK)
        self.assertEqual(result[4].kind, TokenType.NEWLINE)

    def test_operators(self):
        res = self.process_input("+- */ >>= = !=")
        self.assertEqual(len(res), 9)
        self.assertEqual(res[0].kind, TokenType.PLUS)
        self.assertEqual(res[1].kind, TokenType.MINUS)
        self.assertEqual(res[2].kind, TokenType.ASTERISK)
        self.assertEqual(res[3].kind, TokenType.SLASH)
        self.assertEqual(res[4].kind, TokenType.GT)
        self.assertEqual(res[5].kind, TokenType.GTEQ)
        self.assertEqual(res[6].kind, TokenType.EQ)
        self.assertEqual(res[7].kind, TokenType.NOTEQ)
        self.assertEqual(res[8].kind, TokenType.NEWLINE)

    def test_comments(self):
        res = self.process_input("+- # This is a comment!\n */")
        self.assertEqual(len(res), 6)
        self.assertEqual(res[0].kind, TokenType.PLUS)
        self.assertEqual(res[1].kind, TokenType.MINUS)
        self.assertEqual(res[2].kind, TokenType.NEWLINE)
        self.assertEqual(res[3].kind, TokenType.ASTERISK)
        self.assertEqual(res[4].kind, TokenType.SLASH)
        self.assertEqual(res[5].kind, TokenType.NEWLINE)

    def test_string(self):
        res = self.process_input("+- \"This is a string\" # This is a comment!\n */")
        self.assertEqual(len(res), 7)
        self.assertEqual(res[0].kind, TokenType.PLUS)
        self.assertEqual(res[1].kind, TokenType.MINUS)
        self.assertEqual(res[2].kind, TokenType.STRING)
        self.assertEqual(res[2].text, "This is a string")
        self.assertEqual(res[3].kind, TokenType.NEWLINE)
        self.assertEqual(res[4].kind, TokenType.ASTERISK)
        self.assertEqual(res[5].kind, TokenType.SLASH)
        self.assertEqual(res[6].kind, TokenType.NEWLINE)

    def test_string_illegal_char(self):
        self.assertRaises(LexerError, self.process_input, '"Str\n"')
        self.assertRaises(LexerError, self.process_input, '"S\rr\r"')
        self.assertRaises(LexerError, self.process_input, '"S\\tr"')
        self.assertRaises(LexerError, self.process_input, '"St%r"')

    def test_string_quote(self):
        self.assertRaises(LexerError, self.process_input, '"sdfsdf')

    def test_number(self):
        res = self.process_input("+-123 9.8654*/")
        self.assertEqual(len(res), 7)
        self.assertEqual(res[0].kind, TokenType.PLUS)
        self.assertEqual(res[1].kind, TokenType.MINUS)
        self.assertEqual(res[2].kind, TokenType.NUMBER)
        self.assertEqual(res[2].text, "123")
        self.assertEqual(res[3].kind, TokenType.NUMBER)
        self.assertEqual(res[3].text, "9.8654")
        self.assertEqual(res[4].kind, TokenType.ASTERISK)
        self.assertEqual(res[5].kind, TokenType.SLASH)
        self.assertEqual(res[6].kind, TokenType.NEWLINE)

    def test_number_dot_error(self):
        self.assertRaises(LexerError, self.process_input, "12.")

    def check_identifiers(self):
        res = self.process_input("IF+-123 foo*THEN/")
        self.assertEqual(len(res), 9)
        self.assertEqual(res[0].kind, TokenType.IF)
        self.assertEqual(res[1].kind, TokenType.PLUS)
        self.assertEqual(res[2].kind, TokenType.MINUS)
        self.assertEqual(res[3].kind, TokenType.NUMBER)
        self.assertEqual(res[4].text, "123")
        self.assertEqual(res[4].kind, TokenType.IDENT)
        self.assertEqual(res[4].text, "foo")
        self.assertEqual(res[5].kind, TokenType.ASTERISK)
        self.assertEqual(res[6].kind, TokenType.THEN)
        self.assertEqual(res[7].kind, TokenType.SLASH)
        self.assertEqual(res[8].kind, TokenType.NEWLINE)


if __name__ == '__main__':
    unittest.main()
