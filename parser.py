
from log            import *
from parser_utility import *
from statement      import *
from symbol         import *

def primary_expression(it):
    if it.next().kind == TokenKind.IDENTIFIER:
        it.consume()
    
    elif it.next().kind == TokenKind.CONSTANT:
        return Symbols.add_constant(it.consume())
    
    elif it.next().kind == TokenKind.STRING_LITERAL:
        return Symbols.add_string_literal(it.consume())

    else:
        assert False
        it.consume('(')
        expression(it)
        it.consume(')')
        
    
def postfix_expression(it):
    while True:
        base_expr = primary_expression(it)
    
        if it.next().lexeme == '[':
            it.consume('[')
            expr = expression()
            it.consume(']')
            
        elif it.next().lexeme == '(':
            it.consume('(')
            arguments = argument_expression_list(it)
            it.consume(')')
            
        elif it.next().lexeme in ['.', '->']:
            it.consume()
            member = it.consume(TokenKind.IDENTIFIER)
           
        elif it.next().lexeme in ['++', '--']:
           assert False
           it.consume()
        
        else:
            break
    
def argument_expression_list(it):
    if it.next().lexeme != ')':
        assignment_expression()
        while it.next().lexeme == ',':
            it.consume(',')
            assignment_expression()

def unary_expression(it):
    if it.next().lexeme in ['++', '--']:
        it.consume()
        unary_expression(it)
        
    elif it.next().lexeme in ['&', '*', '+', '-', '~', '!']:
        it.consume()
        cast_expression(it)
        
    elif it.next().lexeme == 'sizeof':
        it.consume('sizeof')
        if it.next().lexeme == '(':
            it.consume('(')
            type_name(it)
            it.consume(')')
            
        else:
            unary_expression(it)
            
    else:
        postfix_expression(it)
    
def cast_expression(it):
    if it.next().lexeme == '(' and it.peek().lexeme in TYPE_SPECIFIERS + TYPE_QUALIFIERS + TYPE_NAMES:
        it.consume('(')
        type_name(it)
        it.consume(')')
        cast_expression(it)
        
    else:
        unary_expression(it)

def multiplicative_expression(it):
    cast_expression(it)
    
    while it.next().lexeme in ['*', '/', '%']:
        it.consume()
        cast_expression(it)

def additive_expression(it):
    multiplicative_expression(it)
    
    while it.next().lexeme in ['+', '-']:
        it.consume()
        multiplicative_expression(it)

def shift_expression(it):
    additive_expression(it)
    
    while it.next().lexeme in ['<<', '>>']:
        it.consume()
        additive_expression(it)

def relational_expression(it):
    shift_expression(it)
    
    while it.next().lexeme in ['<', '>', '<=', '>=']:
        it.consume()
        shift_expression(it)

def equality_expression(it):
    relational_expression(it)
    
    while it.next().lexeme in ['==', '!=']:
        it.consume()
        relational_expression(it)

def and_expression(it):
    equality_expression(it)
    
    while it.next().lexeme == '&':
        it.consume('&')
        equality_expression(it)
    
def exclusive_or_expression(it):
    and_expression(it)
    
    while it.next().lexeme == '^':
        it.consume('^')
        and_expression(it)

def inclusive_or_expression(it):
    exclusive_or_expression(it)
    
    while it.next().lexeme == '|':
        it.consume('|')
        exclusive_or_expression(it)

def logical_and_expression(it):
    inclusive_or_expression(it)
    
    while it.next().lexeme == '&&':
        it.consume('&&')
        inclusive_or_expression(it)

def logical_or_expression(it):
    logical_and_expression(it)
    
    while it.next().lexeme == '||':
        it.consume('||')
        logical_and_expression(it)

def conditional_expression(it):
    logical_or_expression(it)
    
    if it.next().lexeme == '?':
        it.consume('?')
        expression(it)
        it.consume(':')
        conditional_expression(it)
        
def assignment_expression(it):
    conditional_expression(it)
    
    if it.next().lexeme in ['=', '*=', '/=', '%=', '+=', '-=', '<<=', '>>=', '&=', '^=', '|=']:
        it.consume()
        assignment_expression(it)

def expression(it):
    assignment_expression(it)
    
    while it.next().lexeme == ',':
        it.consume(',')
        assignment_expression(it)

def constant_expression(it):
    conditional_expression(it)

def declaration(it):
    decl_list = init_declarator_list(it)       
    it.consume(';')
    return decl_list

def declaration_specifiers(it):
    tokens = []
    
    while it.next().lexeme in STORAGE_CLASSES + TYPE_SPECIFIERS + TYPE_QUALIFIERS + TYPE_NAMES:
        tokens.append(it.consume())
    
    return Specifier(tokens)
        
def init_declarator_list(it):
    decl_list = []
    
    if it.next().lexeme != ';':
        decl_list.append(init_declarator(it))
        
        while it.next().lexeme == ',':
            it.consume(',')
            decl_list.append(init_declarator(it))
            
    return decl_list

def init_declarator(it):
    decl_obj = declarator(it)
    
    if it.next().lexeme == '=':
        it.consume('=')
        initializer(it)
        
    return decl_obj

def struct_or_union_specifier(it):
    if it.next().lexeme in ['struct', 'union']:
        it.consume()

        if it.next().kind == IDENTIFIER:
            it.consume()

        if it.next().lexeme == '{':
            it.consume('{')
            struct_declaration_list(it)
            it.consume('}')

def struct_declaration_list(it):
    while it.next().lexeme != '}':
        struct_declaration(it)
    
def struct_declaration(it):
    specifier_qualifier_list(it)
    struct_declarator_list(it)
    it.consume(';')

def specifier_qualifier_list(it):
    while it.next().lexeme in TYPE_SPECIFIERS + TYPE_QUALIFIERS:
        it.consume()

def struct_declarator_list(it):
    struct_declarator(it)
    
    while it.next().lexeme == ',':
        it.consume(',')
        struct_declarator(it)
    
def struct_declarator(it):
    if it.next().lexeme != ':':
        declarator(it)
        
    if it.next().lexeme == ':':
        it.consume(':')
        constant_expression(it)

def enum_specifier(it):
    it.consume('enum')
    
    if it.next().kind == TokenKind.IDENTIFIER:
        it.consume()
        
    if it.next().lexeme == '{':
        it.consume('{')
        enumerator_list(it)
        it.consume('}')

def enumerator_list(it):
    enumerator(it)
    
    while it.next().lexeme == ',':
        it.consume(',')
        enumerator(it)

def enumerator(it):
    it.consume(TokenKind.IDENTIFIER)
    
    if it.next().lexeme == '=':
        it.consume('=')
        constant_expression(it)
        
def declarator(it):
    indirection          = pointer(it)
    decl_obj             = direct_declarator(it)
    decl_obj.indirection = indirection
    
    return decl_obj

def direct_declarator(it):
    name = it.consume(TokenKind.IDENTIFIER)
    array_size  = None
    parameters  = None
    
    if it.next().lexeme == '[':
        it.consume('[')
        
        if it.next().lexeme != ']':
            array_size = constant_expression(it)
            
        it.consume(']')
        
    elif it.next().lexeme == '(':
        it.consume('(')
        parameters = [] if it.next().lexeme == ')' else parameter_type_list(it)
        it.consume(')')
            
    return Declarator(name, array_size, parameters)
            
def pointer(it):
    if it.next().lexeme == '*':
        it.consume('*')
        return 1 + pointer(it)
        
    elif it.next().lexeme in TYPE_QUALIFIERS:
        push_warning(f'ignoring specifier: {it.next().lexeme}')
        type_qualifier_list(it)
        return pointer(it)

    else:
        return 0
        
def type_qualifier_list(it):
    while it.next().lexeme in TYPE_QUALIFIERS:
        it.consume()

def parameter_type_list(it):
    parameters = parameter_list(it)
    
    if it.next().lexeme == ',' and it.peek().lexeme == '...':
        error(it.next().file_info(), 'varadic functions not supported')
        it.consume(',')
        it.consume('...')
        
    assert False
    return parameters

def parameter_list(it):
    parameter_declaration(it)
    
    while it.next().lexeme == ',':
        it.consume(',')
        parameter_declaration(it)

def parameter_declaration(it):
    declaration_specifiers(it)
    
    if it.next().lexeme in ['*'] + TYPE_QUALIFIERS or it.next().kind == TokenKind.IDENTIFIER:
        declarator(it)

def type_name(it):
    specifier_qualifier_list(it)
    
def initializer(it):
    if it.next().lexeme == '{':
        it.consume('{')
        initializer_list()
        if it.next().lexeme == ',':
            it.consume(',')
        it.consume('}')
     
    else:
        assignment_expression(it)

def initializer_list(it):
    initializer(it)
    
    while it.next().lexeme == ',':
        it.consume(',')
        initializer(it)

def statement(it):
    if it.next().lexeme in ['case', 'default'] or it.next().kind == TokenKind.IDENTIFIER and it.peek().lexeme == ':':
        labeled_statement(it)
        
    elif it.next().lexeme == '{':
        compound_statement(it)
        
    elif it.next().lexeme in ['if', 'switch']:
        selection_statement(it)
        
    elif it.next().lexeme in ['while', 'do', 'for']:
        iteration_statement(it)
        
    elif it.next().lexeme in ['goto', 'continue', 'break', 'return']:
        jump_statement(it)
        
    else:
        expression_statement(it)


def labeled_statement(it):
    if it.next().lexeme == 'case':
        it.consume('case')
        constant_expression(it)
        
    elif it.next().lexeme == 'default':
        it.consume('default')
       
    else:
        it.consume(TokenKind.IDENTIFIER)
        
    it.consume(':')
    statement(it)
    

def compound_statement(it):
    it.consume('{')
    
    if it.next().lexeme == '}':
        it.consume('}')
        return EmptyStatement()
        
    else:
        assert False
        
        if is_statement(it):
            statement_list(it)
       
        else:
            declaration_list(it)
            
            if is_statement(it):
                statement_list(it)
                
        it.consume('}')

def declaration_list(it):
    declaration(it)
    
    while not is_statement(it) and it.next().lexeme != '}':
        declaration(it)

def statement_list(it):
    statement(it)
    
    while is_statement(it):
        statement(it)

def expression_statement(it):
    if it.next().lexeme != ';':
        expression(it)
        
    it.consume(';')

def selection_statement(it):
    if it.next().lexeme == 'if':
        it.consume('if')
        it.consume('(')
        expression(it)
        it.consume(')')
        statement(it)
        if it.next().lexeme == 'else':
            it.consume('else')
            statement(it)
  
    else:
        it.consume('switch')
        it.consume('(')
        expression(it)
        it.consume(')')
        statement(it)      

def iteration_statement(it):
    if it.next().token == 'while':
        it.consume('while')
        it.consume('(')
        expression(it)
        it.consume(')')
        statement(it)
        
    elif it.next().token == 'do':
        it.consume('do')
        statement(it)
        it.consume('while')
        it.consume('(')
        expression(it)
        it.consume(')')
        it.consume(';')
        
    else:
        it.consume('for')
        it.consume('(')
        expression_statement(it)
        expression_statement(it)
        if it.next().lexeme != ')':
            expression(it)
        it.consume(')')
        statement(it)

def jump_statement(it):
    if it.next().lexeme == 'goto':
        it.consume('goto')
        it.consume(TokenKind.IDENTIFIER)
        
    elif it.next().lexeme == 'continue':
        it.consume('continue')
        
    elif it.next().lexeme == 'break':
        it.consume('break')
        
    else:
        it.consume('return')
        
        if it.next().lexeme != ';':
            expression(it)
            
    it.consume(';')

def translation_unit(it):
    while it:
        external_declaration(it)
        check_log('<NULL>')

def external_declaration(it):
    file_info = it.next().file_info()
    specifier = declaration_specifiers(it)    
    check_log(file_info)

    try:
        it.push()
        function_definition(it, specifier)
        
    except SyntaxException:
        it.pop()
        clear_log()
        file_info = it.next().file_info()
        decl_list = declaration(it)
        check_log(file_info)
        Symbols.add_variable(specifier, decl_list)

def function_definition(it, specifier):
    decl  = declarator(it)
    stmnt = compound_statement(it)
    Symbols.add_function(specifier, decl, stmnt)
