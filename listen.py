import redis

r = redis.StrictRedis(host='localhost',port=6379,db=0)

var = 1
while var == 1 :
    varvar = r.blpop('outQ')
    dictionary = r.hgetall(varvar[1])
    print dictionary