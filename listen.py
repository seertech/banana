import redis

r = redis.StrictRedis(host='localhost',port=6379,db=0)

var = 1
while var == 1 :
    varvar = r.blpop('outQ')
    response = r.hget(varvar[1],'response')
    print response