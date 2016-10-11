# -*- coding: utf-8 -*-
"""
Instant Messaging Server

Created on Sun Oct  9 11:29:23 2016

@author: Martin Jay McKee
"""

# server.py 
import json
import select
import socket                                         
import threading

import imutil

class IMServer(threading.Thread):
    def __init__(self, host, port=8881, queue=5, debug=False):
        threading.Thread.__init__(self)
        self.__host = host
        self.__port = port    
        self.__queue = queue           
        self.__debug = debug        
        self.__kill = threading.Event()
        self.__clients = {}
        self.start()
        print('IMServer worker thread created and started.')
        
    def close(self):
        self.__kill.set()
    
    def run(self):
        print('Beginning IMServer Main Loop')
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ss.bind((self.__host, self.__port))
        ss.listen(self.__queue)

        try:        
            while not self.__kill.isSet():
                # Add client connections if they are waiting
                rd, _, _ = select.select([ss]+list(self.__clients.keys()), [], [], 0)
                for rs in rd:
                    if rs == ss:
                        # Accept the client connection
                        cs, addr = ss.accept()
                    
                        # Request the client's username
                        self.sendCMD(cs, 'req_username')
                    
                        # Receive the client's username and add the client
                        data = self.receive(cs)
                        try:
                            username = data['username']
                            self.__clients[cs] = (username, addr)
                            self.sendMsg(self.__clients.keys(), '', 'New user {} signed in!'.format(username))
                        except Exception as e:
                            cs.close()
                            if cs in self.__clients: 
                                del self.__clients[cs]
                    else:
                        data = self.receive(rs)
                        if data == None:
                            username, addr = self.__clients[rs]
                            print('Client {} left!'.format(username))
                            del self.__clients[rs]
                            rs.close()                            
                        elif data == {}:
                            pass                            
                        else:
                            if 'cmd' in data:
                                cmd = data['cmd']
                                if cmd == 'req_users':
                                    users = [self.__clients[s][0] for s in self.__clients.keys()]
                                    self.sendMsg([rs], '', '{}'.format(users), private=True)
                                    if self.__debug:
                                        print('Sending requested users list to {}'.format(self.__clients[rs][0]))
                            elif 'message' in data:
                                dest = None if not 'dest' in data else data['dest']
                                msg = None if not 'message' in data else data['message']
                                src = '???' if not 'src' in data else data['src']
    #                            print('dest={}, src={}, msg={}'.format(dest,src,msg))
                                recipiants = []
                                if dest == None: # Sent to all others
                                    recipiants = [s for s in self.__clients.keys() if not s == rs]
                                else:
                                    for s in self.__clients.keys():
                                        username, addr = self.__clients[s]
                                        if dest == username:
                                            recipiants.append(s)
                                self.sendMsg(recipiants, src, msg, private=not(dest==None))
        finally:
            for cs in self.__clients.keys():
                cs.close()
        
    def sendCMD(self, cs, cmd):
        try:
            cs.send(json.dumps({'cmd':cmd}).encode())
        except Exception as e:
            if self.__debug:
                print('Send CMD Exception -- {}'.format(e))

    def sendMsg(self, css, src, message, private=False):
        data = {'src':src, 'message':message, 'private':private}
        try:
            for cs in css:
                cs.send(json.dumps(data).encode())
        except Exception as e:
            if self.__debug:
                print('Send Message Exception --{}'.format(e))                
            
    def receive(self, cs, buffer = 1024):
        try:
            tm = cs.recv(buffer)
        except Exception as e:
            if self.__debug:
                print('Receive Exception -- {}'.format(e))
            return None
        try:
            if len(tm) > 0:
                tm = tm.decode()
                data = json.loads(tm)
                return data
        except Exception as e:
            if self.__debug:
                print('Receive Exception -- {}'.format(e))
        return {}

        
if __name__ == '__main__':
    # TODO: ADD COMMAND-LINE ARGUMENTS TO THIS SO THAT IT DOESN'T NEED TO BE RECOMPILED
    # -P, --port [8881]
    # -H, --host [127.0.0.1 or IP Address]
    # --loopback [false]
    # -Q, --queue [5]
    # -B, --buffer [4096]
    # --debug [false]

#    host = '192.168.1.104'
    host = imutil.default_host
#    host = '172.16.23.81'
    port = imutil.default_port
    server = None
    
    try:
        server = IMServer(host, port=port, debug=True) 
        while True:
            pass
    except KeyboardInterrupt:
        pass
    finally:
        if not server is None:
            print('Closing IMServer')
            server.close()
            server.join()


