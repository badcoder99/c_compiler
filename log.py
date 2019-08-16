
import sys

error_list   = []
warning_list = []  
  
def error(file_info, msg):
    print(f'{file_info}: error: {msg}')
    sys.exit()
  
def clear_log():
    global error_list
    global warning_list
    
    error_list   = []
    warning_list = []  
  
def push_error(msg):
    global error_list
    error_list.append(msg)
    
def push_warning(msg):
    global warning_list
    warning_list.append(msg)
    
def check_log(file_info):
    pop_errors(file_info)
    pop_warnings(file_info)
    
def pop_errors(file_info):
    global error_list
    
    if error_list:
        print(f'{file_info}: error: {error_list[0]}')
        sys.exit()

def pop_warnings(file_info):
    global warning_list
    for warning in warning_list:
        print(f'{file_info}: warning: {warning}')
        
    warning_list = []