#!usr/bin/python
# B.A.N.A.N.A. (Because Another Name Ain't Nothing Ayt)
import redis
import threading
import time
import json
import os
import ConfigParser
import importlib
from flask import Flask, request

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
        print self.moduleDict
        self.bananaAction(self.redis_conn)

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

    def bananaAction(self,r):
        if(r.get('counttwo') is None):
            r.set('counttwo','1')

        var = 1
        while var == 1 :
            varvar = r.blpop('inQ')
            dictionary = r.hgetall(varvar[1])
            message = r.hget(varvar[1],'message')
            gateway = r.hget(varvar[1],'gateway')
            response = self.parse_command(message)
            r.hset('response:'+str(r.get('counttwo')),'response',response)
            r.hset('response:'+str(r.get('counttwo')),'gateway',gateway)
            r.rpush('outQ','response:'+str(r.get('counttwo')))
            r.incr('counttwo')
            if response == "exit":
                break

    # Parses and identifies the command
    def parse_command(self,input):
        tokens = input.split(' ')
        response = 'default'

        if tokens[0] == "banana":
            
            if tokens[1] in self.moduleDict:
                response = self.moduleDict[tokens[1]].run(input)

            else:
                response = 'Module not found!\n'

        elif tokens[0] == "exit":
            response = "exit"

        else:
            response = 'Function not found!\n'

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
        if(r.get('countthree') is None):
            r.set('countthree','1')
        while (1):
            #self.lock.acquire()
            response = self.listenAction(self.redis_conn)
            #self.lock.release()
            #if response == "exit":
                #break
            #time.sleep(1)

    #checks the outQ for response messages
    def listenAction(self,r):
        varvar = r.blpop('outQ')
        response = r.hget(varvar[1],'response')
        gateway = r.hget(varvar[1],'gateway')
        r.hset('response:'+str(r.get('countthree')),'response',response)
        r.hset('response:'+str(r.get('countthree')),'gateway',gateway)
        r.rpush('slackQ','response:'+str(r.get('countthree')))
        r.incr('countthree') 
        return response

##########################################################

r = redis.StrictRedis(host='localhost',port=6379,db=0)

lock = threading.Lock()

sendThread = send(r,lock)
coreThread = core(r)
listenThread = listen(r,lock)

sendThread.start()    
coreThread.start()      
listenThread.start()  

app = Flask(__name__)
@app.route("/listen/", methods=['POST'])
def main():
    username = "banana"
    # ignore message we sent
    msguser = request.form.get("user_name", "").strip()
    print msguser
    if username == msguser or msguser.lower() == "slackbot":
        return ""

    #text = "\n".join(run_hook("message", request.form, {"config": config, "hooks": hooks}))
    #if not text: return ""

    r.hset('command','text',request.form.get("text", ""))
    r.hset('command','gateway','slack')
    r.rpush('mainQ','command')

    varvar = r.blpop('slackQ')

    response = {
        "text": r.hget(varvar[1],'response')
    }

    return json.dumps(response)

if __name__ == "__main__":
    app.run(debug=True, host = '0.0.0.0')
