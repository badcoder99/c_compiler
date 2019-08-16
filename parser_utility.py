
from lexical import *


TYPE_NAMES      = []

TYPE_SPECIFIERS = ['void', 'char', 'short', 'int', 'long', 'float', 
                   'double', 'signed', 'unsigned', 'struct', 'union', 'enum']
                   
TYPE_QUALIFIERS = ['const', 'volatile']   
    
STORAGE_CLASSES = ['typedef', 'extern', 'static', 'auto', 'register']

def is_statement(it):
    return it.next().lexeme in ['case', 'default', 'if', 'switch', 'while', 'sizeof'
                                   'do', 'for', 'goto', 'continue', 'break', 'return',
                                   '(', '{', ';', '++', '--', '&', '*', '+', '-', '~', '!' ] \
           or it.next().kind == TokenKind.IDENTIFIER and it.peek().lexeme == ':' \
           or it.next().kind in [TokenKind.CONSTANT, TokenKind.STRING_LITERAL] \
           or it.next().kind == TokenKind.IDENTIFIER and it.next().lexeme not in TYPE_NAMES

class SyntaxException(Exception):
    pass
           
class Iterator:
    def __init__(self, tokens, filename, linenum):
        self.tokens     = tokens
        self.pos        = 0
        self.len        = len(tokens)
        self.filename   = filename
        self.linenum    = linenum
        self.null_token = NullToken(self.filename, self.linenum)
        self.func_parse = False
        
    def __bool__(self):
        return self.pos < self.len
        
    def push(self):
        self.old_pos = self.pos
        
    def pop(self):
        self.pos = self.old_pos
        
    def next(self):        
        return self.tokens[self.pos] if self.pos < self.len else self.null_token

    def peek(self):
        return self.tokens[self.pos + 1] if self.pos + 1 < self.len else self.null_token
        
    def consume(self, what=None):
        token = self.next()

        if not token:
            Iterator.expected(token, what)
              
        elif isinstance(what, str):
            if token.lexeme != what:
                Iterator.expected(token, what)

        elif isinstance(what, TokenKind):
            if token.kind != what:
                Iterator.expected(token, what)
            
        self.pos += 1
        return token
           
    def expected(token, what):
        found = token.lexeme if token else 'end of file'
        msg   = f'{token.filename}:{token.linenum}: error: found ' \
                f'{found} expecting {what}'
    
        raise SyntaxException(msg)