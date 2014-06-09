import redis
import threading

#################
# CORE THREAD   #
#################
class core(threading.Thread):
    def __init__(self,redis_conn):
        threading.Thread.__init__(self)
        self.redis_conn = redis_conn

    def run(self):
        bananaAction(self.redis_conn)

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
        
        if tokens[1] == "logout":
            response = logout()

        if tokens[1] == "basecamp":
            pass

    elif tokens[0] == "exit":
        response = "exit"

    return response


# logouts the current user
def logout():
    global logged_user
    if logged_user is not None:
        logged_user = None
        return notif['notif_logout_success']
    else:
        return error['error_double_logout']


# checks credentials and login user
def login(tokens):

    global logged_user

    correct_credentials = False

    for user in db_user.items():
        if user[1]['username'] == tokens[2] and user[1]['password'] == tokens[3]:

            correct_credentials = True
            
            if  logged_user is not None:
                return error['error_already_logged']

            elif user[1]['username'] == logged_user:
                return error['error_already_logged']

            else:
                logged_user = user[1]['username']
                return notif['notif_login_success']

    if not correct_credentials:
        return error['error_login']

#################
# SEND THREAD   #
#################
class send(threading.Thread):
    def __init__(self, redis_conn):
        threading.Thread.__init__(self)
        self.redis_conn = redis_conn

    def run(self):
        sendAction(self.redis_conn)

def sendAction(r):
    #if count is undeclared, initialize it to 1
    if(r.get('count') is None):
        r.set('count','1')

    while (1):
        command = raw_input("Enter a message: ")
        r.hset('command:'+str(r.get('count')),'message',command)
        r.rpush('inQ','command:'+str(r.get('count')))
        r.incr('count') 
        if command == 'exit':
            break

#################
# LISTEN THREAD #
#################
class listen(threading.Thread):
    def __init__(self, redis_conn):
        threading.Thread.__init__(self)
        self.redis_conn = redis_conn
    def run(self):
        listenAction(self.redis_conn)

#checks the outQ for response messages
def listenAction(r):
    var = 1
    while var == 1 :
        varvar = r.blpop('outQ')
        response = r.hget(varvar[1],'response')
        print response
        if response == "exit":
            break


##########################################################

#   Temporary values for testing.

##########################################################

logged_user = None

# Hardcoded user credentials for logging in
db_user = {
    1 : {
        'username' : 'admin',
        'password' : 'password'
    },

    2 : {
        'username' : 'foo',
        'password' : 'bar'
    }
}

# Hardcoded error message
error = {
    'error_unknown' : 'Unknown Command.',
    'error_syntax' : 'Syntax Error.',
    'error_already_logged' : 'You are already logged in. Log current account first.',
    'error_double_logout' : 'You are not logged in in the first place.',
    'error_login' : 'User does not exsist or username and password is incorrect.',
}

# Hardcoded notif message
notif = {
    'notif_login_success' : 'Login Success',
    'notif_logout_success' : 'You have been successfully logged out.',
}

##########################################################

r = redis.StrictRedis(host='localhost',port=6379,db=0)

coreThread = core(r)
listenThread = listen(r)
sendThread = send(r)

coreThread.start()      
listenThread.start()
sendThread.start()      
