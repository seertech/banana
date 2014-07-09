#!usr/bin/python
# B.A.N.A.N.A. (Because Another Name Ain't Nothing Ayt)
import redis
import threading
#import time
import os
import ConfigParser
import importlib
import requests
import json

#################
# CORE THREAD   #
#################
class core(threading.Thread):
    def __init__(self,redis_conn):
        threading.Thread.__init__(self)
        self.redis_conn = redis_conn
        self.moduleDict = {}
        #looks into modules folder. 
        modules = os.listdir("modules")
        config = ConfigParser.RawConfigParser()
        for module in modules:
            #we assume that the module folder only includes _init_.py,_init_.pyc, and more module folders
            if module != "__init__.py" and module != "__init__.pyc":
                files = os.listdir("modules/" + module)

                cfg_Flag = False

                #looks for the cfg file
                for data in files:
                    #we assume that the files have the same name with the folder
                    #we assume that there are .cfg and .py files in the folder.
                    #the .py must have a class with name the same as the filename
                    #the .py must have a class function run(input)
                    if data[len(data)-4:len(data)] == ".cfg":
                        cfg_Flag = True
                        config.read("modules/" + module + "/" + data)
                        key = config.get('Setup','keyword')
                        value = importlib.import_module('.' + module,'modules.' + module)
                        class_ = getattr(value,module.capitalize())
                        test = class_()
                        self.moduleDict[key] = test

                if not cfg_Flag:
                    self.createCFG(module) 

    def run(self):
        if(self.redis_conn.get('counttwo') is None):
            self.redis_conn.set('counttwo','1')

        while (1):
            varvar = self.redis_conn.blpop('inQ')
            dictionary = self.redis_conn.hgetall(varvar[1])
            message = self.redis_conn.hget(varvar[1],'message')
            gateway = self.redis_conn.hget(varvar[1],'gateway')
            sender = self.redis_conn.hget(varvar[1],'sender')

            worker = Worker(self.redis_conn,self.moduleDict,message,gateway,sender)
            worker.start()

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

class Worker(threading.Thread):
    def __init__(self,r,moduleDict,message,gateway,sender):
        threading.Thread.__init__(self)
        self.r = r
        self.moduleDict = moduleDict
        self.message = message
        self.gateway = gateway
        self.sender = sender

    def run(self):
        tokens = self.message.split(' ')
        response = 'default'

        if tokens[0] == "banana::":
                
            if tokens[1] in self.moduleDict:
                response = self.moduleDict[tokens[1]].run(self.message,self.sender)

            else:
                response = 'Module not found!\n'

        elif tokens[0] == "exit":
            response = "exit"

        else:
            response = 'Function not found!\n'
        
        self.r.hset('response:'+str(self.r.get('counttwo')),'response',response)
        self.r.hset('response:'+str(self.r.get('counttwo')),'gateway',self.gateway)
        self.r.hset('response:'+str(self.r.get('counttwo')),'sender',self.sender)
        self.r.rpush('outQ','response:'+str(self.r.get('counttwo')))
        self.r.incr('counttwo')

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
        if(self.redis_conn.get('count') is None):
            self.redis_conn.set('count','1')
        while (1):
            #self.lock.acquire()
            command = self.sendAction(self.redis_conn)
            #self.lock.release()
            if command == 'exit':
                break
            #time.sleep(1)


    def sendAction(self,r):
        message = r.blpop('mainQ')
        command = r.hget(message[1],'text')
        gateway = r.hget(message[1],'gateway')
        r.hset('command:'+str(r.get('count')),'message',command)
        r.hset('command:'+str(r.get('count')),'gateway',gateway)
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
        if(self.redis_conn.get('countthree') is None):
            self.redis_conn.set('countthree','1')
        while (1):
            #self.lock.acquire()
            response = self.listenAction(self.redis_conn)
            #self.lock.release()
            if response == "exit":
                break
            #time.sleep(1)

    #checks the outQ for response messages
    def listenAction(self,r):
        varvar = r.blpop('outQ')
        response = r.hget(varvar[1],'response')
        gateway = r.hget(varvar[1],'gateway')
        sender = r.hget(varvar[1],'sender')
        
        if gateway == 'slack':
            self.sendSlack(response)

        print response
        return response

    def sendSlack(self,response):

        postparams = {"channel": "#testingbot", "username": "banana", "text": response }
        getparams = {"token":"PBD7gPUVByYLziBPQ4XkrjvJ"}
        req = requests.post('https://seertech.slack.com/services/hooks/incoming-webhook?token=PBD7gPUVByYLziBPQ4XkrjvJ',params=getparams,data=json.dumps(postparams))
