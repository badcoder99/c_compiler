
from lexical import *
from log     import *

class Declarator:
    def __init__(self, name, array_size, parameters):
        assert not (array_size and parameters)
        
        self.name        = name
        self.array_size  = array_size
        self.parameters  = parameters
        self.indirection = 0 
        
    def __str__(self):
        assert not self.array_size
        
        pointers = '*' * self.indirection
        
        if isinstance(self.parameters, list):
            assert len(self.parameters) == 0
            
            return f'{pointers}{self.name.lexeme}()'
            
        else:
            return f'{pointers}{self.name.lexeme}'

class Specifier:
    def __init__(self, tokens):
        self.signed    = False
        self.unsigned  = False
        self.type_list = []
        
        for token in tokens:
            self.add(token.lexeme)
            
        self.check()
        
    def __str__(self):
        result = ''
        
        if self.signed:
            result += 'signed '
        elif self.unsigned:
            result += 'unsigned '
            
        for type in self.type_list:
            result += f'{type} '
            
        return result
        
    def check(self):
        if self.signed and self.unsigned:
            push_error(f'both signed and unsigned specifiers')
            
        if self.signed or self.unsigned:
            sign       = 'signed' if self.signed else 'unsigned' 
            mismatched = [type for type in self.type_list if type in ['void', 'float', 'double', 'struct', 'union', 'enum']]
            if mismatched:
                push_error(f'both {sign} and {mismatched[0]} specifiers')
        
            base_type = [type for type in self.type_list if type in ['char', 'short', 'int', 'long']]
            if not base_type:
                self.type_list.append('int')
                
                
        if self.type_list.count('long') == 0:
            if len(self.type_list) > 1:
                push_error(f'both {self.type_list[0]} and {self.type_list[1]} specifiers')
                
        elif self.type_list.count('long') == 1:
            mismatched = [type for type in self.type_list if type not in ['double', 'int', 'long']]
            if mismatched:
                push_error(f'too many long specifiers')
                
        elif self.type_list.count('long') == 2:
            mismatched = [type for type in self.type_list if type not in ['int', 'long']]
            if mismatched:
                push_error(f'too many long specifiers')
                
        else:
            push_error(f'too many long specifiers')
            
        if not self.type_list:
            push_error(f'missing type specifier')
        
        
    def add(self, specifier):
        if specifier in ['typedef', 'extern', 'auto', 'register', 'static', 'volatile', 'const']:
            push_warning(f'ignoring specifier: {specifier}')
            
        elif specifier == 'signed':
            if self.signed:
                push_warning(f'ignoring duplicate specifier: signed')
            else:
                self.signed = True
                
        elif specifier == 'unsigned':
            if self.unsigned:
                push_warning(f'ignoring duplicate specifier: unsigned')
            else:
                self.unsigned = True
                
        else:
            if specifier in self.type_list and specifier != 'long':
                push_error(f'duplicate specifier: {specifier}')
            else:
                self.type_list.append(specifier)
          
class Constant:
    def __init__(self, token):
        self.id    = None
        self.value = token.lexeme.lower()
        self.type  = self.get_type()
        
    def __str__(self):
        return f'{self.type} {self.value}'
        
    def __eq__(self, other):
        if not isinstance(other, Constant):
            raise NotImplementedError
         
        else:
            return self.type == other.type and self.value == other.value
    
    def get_type(self):
        lexeme = self.value
                    
        digits   = sum(1 for char in lexeme if char.isdigit())
        period   = lexeme.count('.')
        exponent = lexeme.count('e')        
        float    = lexeme.count('f')
        long     = lexeme.count('l')
        unsigned = lexeme.count('u')   
        hex      = lexeme.find('0x') == 0

        if lexeme[0] == '\'':
            return 'char'
        
        if unsigned > 1:
            error(token.file_info(), f'invalid suffix: {token.lexeme}')
        
        if period or (exponent and not hex):
            if float and long:
                error(token.file_info(), f'invalid suffix: {token.lexeme}')
                
            elif float:
                return 'float'
                
            elif long:
                return 'long double'
                
            else:
                return 'double'
               
        elif long == 0:
            if unsigned:
                return 'unsigned int'
            else:
                return 'int'
                  
        elif long == 1:
            if unsigned:
                return 'unsigned long int'
            else:
                return 'long int'
                
        elif long == 2:
            if unsigned:
                return 'unsigned long long int'
            else:
                return 'long long int'
            
        else:
            error(token.file_info(), f'invalid suffix: {token.lexeme}')
            
class StringLiteral:
    def __init__(self, token, id):
        self.id    = id
        self.value = token.lexeme      
        
    def __eq__(self, other):
        if not isinstance(other, StringLiteral):
            raise NotImplementedError
         
        else:
            return self.value == other.value
            
    def __str__(self):
        return f'{self.value}'
    
    
class Function:
    def __init__(self, specifier, declarator, statement, id):
        self.specifier  = specifier
        self.declarator = declarator
        self.statement  = statement
        self.id         = id
        
    def __str__(self):
        return f'{self.specifier}{self.declarator}\n' \
               f'  {self.statement}'
        
class Variable:
    def __init__(self, specifier, declarator, id):
        self.specifier  = specifier
        self.declarator = declarator
        self.id         = id
        
    def __str__(self):
        return f'{self.specifier}{self.declarator}'
       
class Symbols:
    variables       = []
    functions       = []
    constants       = [] 
    string_literals = []
    next_id         = 0
    
    def view_all():
        print('<Constants>')
        for constant in Symbols.constants:
            print(f'{constant}')
            
        print()
        print('<Functions>')
        for function in Symbols.functions:
            print(f'{function}')
        
        print()        
        print('<StringLiterals>')
        for string_literal in Symbols.string_literals:
            print(f'{string_literal}')
            
        print()
        print('<Variables>')
        for variable in Symbols.variables:
            print(f'{variable}')
    
    def get_next_id():
        id = Symbols.next_id
        Symbols.next_id += 1
        return id
    
    def add_constant(token):        
        constant = Constant(token) 
        if constant not in Symbols.constants:
            constant.id = Symbols.get_next_id()
            Symbols.constants.append(constant)
        return [item for item in Symbols.constants if item == constant][0]
        
    def add_string_literal(token):
        string_literal = StringLiteral(token, Symbols.get_next_id())
        Symbols.string_literals.append(string_literal)
        string_literal
        
    def add_variable(specifier, decl_list):
        for declarator in decl_list:
            Symbols.variables.append(Variable(specifier, declarator, Symbols.get_next_id()))
        
    def add_function(specifier, decl, stmnt):
        function = Function(specifier, decl, stmnt, Symbols.get_next_id())
        Symbols.functions.append(function)
        return function