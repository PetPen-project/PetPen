import redis
import pickle

def push(data):
    r = redis.StrictRedis('localhost', port=6379, db=0)
    res = r.rpush('petpen', pickle.dumps(data))
    if res > 0:
        return 0
    else:
        return 1

def pop():
    r = redis.StrictRedis('localhost', port=6379, db=0)
    res = r.lpop('petpen')
    return pickle.loads(res)

def jobs():
    r = redis.StrictRedis('localhost', port=6379, db=0)
    res = r.llen('petpen')
    return res
