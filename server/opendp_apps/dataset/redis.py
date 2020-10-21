import os

import redis


class RedisClient(object):
    """
    Wrapper around the Redis client
    that handles instance parameters
    (host, etc.) automatically
    """
    def __init__(self):
        self.r = redis.Redis(
            host=os.environ.get('REDIS_HOST'),
            port=os.environ.get('REDIS_PORT'),
            password=os.environ.get('REDIS_PASSWORD'))

    def set(self, key, value):
        return self.r.set(key, value)

    def get(self, key):
        return self.r.get(key)