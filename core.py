#!usr/bin/python
# B.A.N.A.N.A. (Because Another Name Ain't Nothing Ayt)
import redis
import threading
import time
import os
import ConfigParser
import importlib
from basecamp_module import Basecamp_module

#################
# CORE THREAD   #
#################
class core(threading.Thread):
    def __init__(self,redis_conn):
        threading.Thread.__init__(self)
        self.redis_conn = redis_conn
        self.moduleDict = {}
        modules = os.listdir("modules")
        config = ConfigParser.RawConfigParser()
        for module in modules:
            if module != "__init__.py" and module != "__init__.pyc":
                files = os.listdir("modules/" + module)

                cfg_Flag = False

                for data in files:
                    if data[len(data)-4:len(data)] == ".cfg":
                        cfg_Flag = True
                        config.read("modules/" + module + "/" + data)
                        key = config.get('Setup','keyword')
                        value = importlib.import_module('.' + module,'modules.' + module)
                        print value
                        class_ = getattr(value,module.capitalize())
                        test = class_()
                        test.printf()
                        self.moduleDict[key] = test

                if not cfg_Flag:
                    self.createCFG(module) 

    def run(self):
        #self.moduleDict['module1'].printf()
        bananaAction(self.redis_conn)

    def createCFG(self,module):
        config = ConfigParser.RawConfigParser()
        config.add_section('Setup')
        config.set('Setup','keyword',module)

        with open('modules/' + module + '/' + module+'.cfg','wb') as configfile:
            config.write(configfile)

        value = importlib.import_module('.' + module,'modules.' + module)
        class_ = getattr(value,module.capitalize())
        test = class_()
        self.moduleDict[module] = test

def bananaAction(r):
    if(r.get('counttwo') is None):
        r.set('counttwo','1')

    var = 1
    while var == 1 :
        varvar = r.blpop('inQ')
        dictionary = r.hgetall(varvar[1])
        message = r.hget(varvar[1],'message')
        response = parse_command(message)
        r.hset('response:'+str(r.get('counttwo')),'response',response)
        r.rpush('outQ','response:'+str(r.get('counttwo')))
        r.incr('counttwo')
        if response == "exit":
            break

# Parses and identifies the command
def parse_command(input):
    tokens = input.split(' ')
    response = 'default'

    if tokens[0] == "banana":
        
        if tokens[1] == "login":
            response = login(tokens)
        
        elif tokens[1] == "logout":
            response = logout()

        elif tokens[1] == "basecamp":
            response = basecampFunction(tokens)

    elif tokens[0] == "exit":
        response = "exit"

    return response

#################
# SEND THREAD   #
#################
class send(threading.Thread):
    def __init__(self, redis_conn,lock):
        threading.Thread.__init__(self)
        self.redis_conn = redis_conn
        self.lock = lock
    def run(self):
        #if count is undeclared, initialize it to 1
        if(r.get('count') is None):
            r.set('count','1')
        while (1):
            self.lock.acquire()
            command = sendAction(self.redis_conn)
            self.lock.release()
            if command == 'exit':
                break
            time.sleep(1)


def sendAction(r):
    command = raw_input("Enter a message: ")
    r.hset('command:'+str(r.get('count')),'message',command)
    r.rpush('inQ','command:'+str(r.get('count')))
    r.incr('count') 
    return command

#################
# LISTEN THREAD #
#################
class listen(threading.Thread):
    def __init__(self, redis_conn,lock):
        threading.Thread.__init__(self)
        self.redis_conn = redis_conn
        self.lock = lock
    def run(self):
        while (1):
            self.lock.acquire()
            response = listenAction(self.redis_conn)
            self.lock.release()
            if response == "exit":
                break
            time.sleep(1)

#checks the outQ for response messages
def listenAction(r):
    varvar = r.blpop('outQ')
    response = r.hget(varvar[1],'response')
    print response
    return response

##########################################################

if __name__ == "__main__":

    r = redis.StrictRedis(host='localhost',port=6379,db=0)

    lock = threading.Lock()

    sendThread = send(r,lock)
    coreThread = core(r)
    listenThread = listen(r,lock)

    sendThread.start()    
    coreThread.start()      
    listenThread.start()  
