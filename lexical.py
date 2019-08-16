
from enum import Enum, auto
import regex as re 
import sys

P  = r'(/\*[^(*/)]*(\*/)?|\*/|//.*)|' \
     r'([0-9]*\.[0-9]+[Ee][+-]?[0-9]+[fFlL]?|' \
     r'[0-9]+\.[0-9]*[Ee][+-]?[0-9]+[fFlL]?|' \
     r'[0-9]*\.[0-9]+[fFlL]?|' \
     r'[0-9]+\.[0-9]*[fFlL]?|' \
     r'[0-9]+[Ee][+-]?[0-9]+[fFlL]?|' \
     r'0[xX][a-fA-F0-9]+[uUlL]*|' \
     r'[0-9]+[uUlL]*' \
     r'|[a-zA-Z_][a-zA-Z0-9_]*|' \
     r'[a-zA-Z_]?\'\\?.\'|' \
     r'\.\.\.|>>=|<<=|\+=|-=|\*=|/=|%=|&=|\^=|\|=|>>|<<|\+\+|--|' \
     r'->|&&|\|\||<=|>=|==|!=|;|\{|\}|,|:|=|\(|\)|\[|\]|\.|&|!|~|-|' \
     r'\+|\*|/|%|<|>|\^|\||\?)|' \
     r'("(\\"|[^"])*")|' \
     r'(\S)'

KEYWORDS = ['auto', 'break', 'case', 'char', 'const', 'continue', 'default', 
    'do', 'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if', 
    'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof', 
    'static', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'void', 
    'volatile', 'while'] 

SYMBOLS = ['...', '>>=', '<<=', '+=', '-=', '*=', '/=', '%=', '&=', '^=', 
    '|=', '>>', '<<', '++', '--', '->', '&&', '||', '<=', '>=', '==',
    '!=', ';', '{', '}', ',', ':', '=', '(', ')', '[', ']', '.', '&', 
    '!', '~', '-', '+', '*', '/', '%', '<', '>', '^', '|', '?']
    
class TokenKind(Enum):
    CONSTANT       = auto()
    IDENTIFIER     = auto()
    STRING_LITERAL = auto()
    KEYWORD        = auto()
    SYMBOL         = auto()
    END_OF_FILE    = auto()
    
class Token:
    def __init__(self, filename, linenum, lexeme):
        self.filename = filename
        self.linenum  = linenum
        self.lexeme   = lexeme
        self.kind     = Token.get_kind(self.lexeme)
        
    def file_info(self):
        return f'{self.filename}:{self.linenum}'
        
    def __str__(self):
        return f'{self.file_info()}: \'{self.lexeme}\' ({self.kind})'
            
    def get_kind(lexeme):
        if lexeme in KEYWORDS:
            return TokenKind.KEYWORD
            
        elif lexeme in SYMBOLS:
            return TokenKind.SYMBOL
            
        elif lexeme[0].isalpha() or lexeme[0] == '_':
            return TokenKind.IDENTIFIER
            
        elif lexeme[0] == '\"':
            return TokenKind.STRING_LITERAL
        
        else:
            return TokenKind.CONSTANT 
    
class NullToken:
    def __init__(self, filename, linenum):
        self.filename = filename
        self.linenum  = linenum
        self.lexeme   = ''
        self.kind     = TokenKind.END_OF_FILE 

    def __str__(self):
        return f'{self.filename}:{self.linenum}: end of file'

    def __bool__(self):
        return False

def read_tokens(filename):
    try:
        tokens = []
        p = re.compile(P)
        with open(filename, 'r') as file:
            linenum = 0
            comment = False
            for line in file.readlines():
                linenum += 1
                
                if line[-1:] == '\n':
                    line = line[0:-1]
              
                for token in re.findall(p, line):
                    if token[0]:
                        if token[0][0:2] == '/*':
                            if token[0][-2:] == '*/':
                                comment = False
                            else:
                                comment = True
                                
                        elif token[0][0:2] == '*/':
                            if comment:
                                comment = False
                            else:
                                print(f'{filename}:{linenum}: error: unexpected token \'*/\'')                             
                                sys.exit()
                                
                    elif comment:
                        continue
                        
                    elif token[2]:
                        tokens.append(Token(filename, linenum, token[2]))
                        
                    elif token[3]:
                        tokens.append(Token(filename, linenum, token[3]))
                        
                    else:
                        print(f'{filename}:{linenum}: error: unexpected token \'{token[5]}\'')                             
                        sys.exit()
                      
            
    except IOError:
        print(f'{filename}: error: no such file')
        sys.exit()
 
    return (tokens, linenum)
