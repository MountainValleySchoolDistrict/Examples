# -*- coding: utf-8 -*-
"""
Created on Sun Oct  9 19:25:02 2016

@author: martin
"""

default_host = '127.0.0.1'
default_port = 8881

def Prompt(message, default=None, val=None, validate=None, errmsg=None):
    if val is None:
        if not default is None:
            val = type(default)
        else:
            val = str
            
    while True:    
        try:
            value = None
            prompt = message if default is None else '{} [{}]'.format(message, default)
            print('{}: '.format(prompt), end='')
            input_string = input().strip()
            if len(input_string) > 0:
                value = val(input_string)
            else:
                if not default is None:
                    value = default
            
            if not validate is None:
                if validate(value):
                    return value
            elif not value == None:
                    return value
        except Exception as e:
            print(e)
            if not errmsg is None:
                print(errmsg)


def LoadFile(filename):
    msg = None
    with open(filename, 'rb') as file:
        msg = file.read().decode()
        lines = msg.split('\n')
        print('Loading ({}):\n'.format(filename))
        for line in lines:
            print('*\t'+line)
    return msg