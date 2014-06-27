from flask import Flask, request
import threading
import core
import redis
import pycurl
import cStringIO
import json

#FLASK SLACK LISTENER
app = Flask(__name__)
@app.route("/listen/", methods=['POST'])
def slack():
    username = "banana"
    msguser = request.form.get("user_name","")
    if username == msguser or msguser.lower() == "slackbot":
        return ""


    slackid = request.form.get("user_id", "")
    user_email = ''


    buf = cStringIO.StringIO()

    c = pycurl.Curl()
    print "CURL!!!"
    c.setopt(c.URL,'https://slack.com/api/users.list?token=xoxp-2315794369-2395812124-2401574040-f0d1b3&pretty=1')
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.perform()
    
    userlist = json.loads(buf.getvalue())
    buf.close()

    for user in userlist['members']:
        if user['id'] == slackid:
            user_email = user['profile']['email']

    r.hset('command','message',request.form.get("text", ""))
    r.hset('command','gateway','slack')
    r.hset('command','sender',user_email)
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