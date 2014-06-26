from flask import Flask, request
import threading
import core
import redis

#FLASK SLACK LISTENER
app = Flask(__name__)
@app.route("/listen/", methods=['POST'])
def slack():
    username = "banana"
    msguser = request.form.get("user_name","")
    if username == msguser or msguser.lower() == "slackbot":
        return ""

    r.hset('command','message',request.form.get("text", ""))
    r.hset('command','gateway','slack')
    r.rpush('inQ','command')

    return ""

@app.route("/oauth2callback")
def oauth():
    print "GMAIL AUTH"
    return ""

if __name__ == "__main__":
    r = redis.StrictRedis(host='localhost',port=6379,db=0)

    lock = threading.Lock()

    #sendThread = core.send(r,lock)
    coreThread = core.core(r)
    listenThread = core.listen(r,lock)

    #sendThread.start()    
    coreThread.start()      
    listenThread.start()  

    app.run(debug=True, host = '0.0.0.0')