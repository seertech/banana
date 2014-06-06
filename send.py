import redis

#establish a connection to the redis database
redis_conn = redis.StrictRedis(host='localhost',port=6379,db=0)

#if count is undeclared, initialize it to 1
if(redis_conn.get('count') is None):
    redis_conn.set('count','1')

while (1):
    command = raw_input("Enter a message: ")
    print command
    if (command == 'exit'):
   	    break
    redis_conn.hset('command:'+str(redis_conn.get('count')),'message',command)
    redis_conn.rpush('inQ','command:'+str(redis_conn.get('count')))
    redis_conn.incr('count')	
   	