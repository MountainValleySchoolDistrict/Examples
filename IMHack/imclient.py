# -*- coding: utf-8 -*-
"""
Created on Sun Oct  9 11:31:05 2016

@author: martin
"""

# client.py  
import json
import select
import socket
import string
import threading

import imutil
           
           
class IMClient:
    def __init__(self, username, host, port, buffer=4096, global_env ={}, local_env={}, allow_exec=False):
        self.__username = username        
        self.__buffer = buffer
        self.__allow_exec = allow_exec
        self.__global_env = global_env
        self.__local_env = local_env
        
        if allow_exec:
            print('Connecting to server on {}:{} -- Warning, remote execution enabled!'.format(host, port))            
        else:
            print('Connecting to server on {}:{}'.format(host, port))
            
        # create a socket object
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    
        # connection to hostname on the port.
        ss.connect((host, port))                               
    
        # Receive the username request
        tm = ss.recv(self.__buffer)        
        tm = tm.decode()
        data = json.loads(tm)
        try:
            cmd = data['cmd']
            if cmd == 'req_username':
                ss.send(json.dumps({'username':username}).encode())
        except:
            raise('Failed to connect!')
        print("IM Connect Complete!")    
        self.__ss = ss        
        
        self.__kill_receive = threading.Event()
        self.__receive_thread = threading.Thread(target=self.__processReceived, args=([self.__ss], self.__kill_receive))
        self.__receive_thread.start()

    def close(self):
        self.__kill_receive.set()
        self.__receive_thread.join()
        self.__ss.close()

    def Send(self, msg, is_file=False):
        msg = msg.strip()        
        data = {'src':self.__username}
        
        execute = (msg[0] == '{') and (msg[-1] == '}')
        if execute:
            data = None
            self.__exec(msg) # NOTE: THIS MAY STILL BE DANGEROUS... NEED TO CHECK IF THIS IS REACHABLE WITHOUT REMOTE EXECUTION ENABLED
        elif msg[0] in set('#@'):
            head, special, tail = self.__partitionSpecial(msg)
            
            data['message'] = tail if not is_file else imutil.LoadFile(tail)
            
            if head == '@':
                if (len(special) > 0) and (not special == '*'):
                    data['dest'] = special
            elif head == '#':
                if special == 'quit':
                    self.close()
                    exit()
                elif special == 'users':
                    data = {'cmd':'req_users'}
        else:
            data['message'] = msg if not is_file else imutil.LoadFile(msg)
            
        if (not data is None) and ('message' in data):
            self.__ss.send(json.dumps(data).encode())
            
    def __partitionSpecial(self, msg):
        head = special = tail = None
        end_index = None
        for index, c in enumerate(msg):
            if index == 0:
                head = c
            if c in string.whitespace:
                end_index = index
                break       
        end_index = len(msg) if end_index is None else end_index
        special = msg[1:end_index]
        tail = msg[end_index:].strip() if end_index < (len(msg)-1) else ''
        return head, special, tail
        
    def __processReceived(self, css, kill):
        while not kill.isSet():
            # Read from the server
            rd, _, _ = select.select(css,[],[],0)
            for cs in rd:
                try:
                    tm = cs.recv(self.__buffer)                                     
                    if len(tm) > 0:
                        tm = tm.decode()
                        try:
                            data = json.loads(tm)
                            prefix = '' if not data['private'] else '*** '
                            msg = data['message'].strip()
                            execute = (msg[0] == '{') and (msg[-1] == '}')
                            if execute:
                                if self.__allow_exec:  # NOTE: THIS IS ***UBER*** DANGEROUS -- THIS SHOULD *ONLY* BE USED IN A SANDBOXED ENVIRONMENT
                                    self.__exec(msg, echo_errors=False)
                                else:
                                    self.Send('Remote Execution on {} disabled.  Sorry!'.format(self.__username))
                            else:
                                if not 'src' in data or data['src'] == '':
                                    print('{prefix}{message}'.format(prefix=prefix, **data))                            
                                else:
                                    print('{prefix}{src} says: {message}'.format(prefix=prefix, **data))
                        except:
                            pass    
                except:
                    pass
        
    def __exec(self, msg, echo_errors=True):
        code = msg[1:-1]
        try:
            print('EXECUTING -- {}'.format(code))
            exec(code, self.__global_env, self.__local_env)
        except Exception as e:
            if echo_errors:
                print(e)
    
    

if __name__ == '__main__':
    username = imutil.Prompt('Username') # TODO: THIS NEEDS TO HAVE A VALIDATE METHOD ADDED TO IT    
    host = imutil.Prompt('Server address', default=imutil.default_host)
    port = imutil.Prompt('Server port', default=imutil.default_port)
    
    try:
        client = IMClient(username, host, port, global_env=globals(), local_env=locals(), allow_exec=True)
    
        while True:        
            # Send Messages
            msg = imutil.Prompt('{}: '.format(username))
            client.Send(msg)
    finally:
        client.close()
        print('Closing IM Client!')
