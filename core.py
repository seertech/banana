import redis

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
    'error_login' : 'User does not exsist or username and password is incorrect.',
}

# Hardcoded notif message
notif = {
    'notif_login_success' : 'Login Success',
    'notif_logout_success' : 'You have been successfully logged out.',
}


##########################################################

logged_user = None

##########################################################

# Parses and identifies the command
def parse_command(input):
    tokens = input.split(' ')

    if tokens[0] == "banana":
        
        if tokens[1] == "login":
            login(tokens)
        
        if tokens[1] == "logout":
            logout()

        if tokens[1] == "basecamp":
            pass


#
def logout():

    logged_user = None
    print notif['notif_logout_success']


# checks credentials and login user
def login(tokens):

    global logged_user

    correct_credentials = False

    for user in db_user.items():
        if user[1]['username'] == tokens[2] and user[1]['password'] == tokens[3]:

            correct_credentials = True
            
            if  logged_user is not None:
                print error['error_already_logged']

            elif user[1]['username'] == logged_user:
                print error['error_already_logged']

            else:
                logged_user = user[1]['username']
                print notif['notif_login_success']

    if not correct_credentials:
        print error['error_login']


##########################################################

r = redis.StrictRedis(host='localhost',port=6379,db=0)

parse_command()

var = 1
while var == 1 :
    varvar = r.blpop('inQ')
    dictionary = r.hgetall(varvar[1])
    message = r.hget(varvar,'message')
    parse_command(message)