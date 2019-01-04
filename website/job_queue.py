import redis
import pickle

def push_(id, data, queue_name):
    r = redis.StrictRedis('localhost', port=6379, db=0)
    res = r.rpush(queue_name, pickle.dumps((id, data)))
    if res > 0:
        return 0
    else:
        return 1

def push(id, data):
    return push_(id, data, 'petpen_wait')

def kill(id):
    return push_(id, '', 'petpen_terminate')

def pop_(queue_name):
    r = redis.StrictRedis('localhost', port=6379, db=0)
    res = r.lpop(queue_name)
    return pickle.loads(res)

def jobs_(queue_name):
    r = redis.StrictRedis('localhost', port=6379, db=0)
    res = r.llen(queue_name)
    return res
