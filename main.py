
from lexical import *
from parser  import *
from symbol  import *

import sys


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 main.py <filename>')
        sys.exit()

    for filename in sys.argv[1:]:
        if len(filename) > 2 and filename[-2:] == '.c':
            tokens, linenum = read_tokens(filename)
            
            it = Iterator(tokens, filename, linenum)
            
            try:
                translation_unit(it)
                Symbols.view_all()
                
            except SyntaxException as e:
                print(e)
        else:
            print(f'{filename}: error: invalid file format')
            sys.exit()
    
