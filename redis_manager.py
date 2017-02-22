__author__ = 'ratnesh.mishra'

import aioredis as redis

class RedisManager:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.conn = None

    def _get_conn(self):
        # This creates single connection while we can go for a connection pool
        return (yield from redis.create_connection((self.redis_host, self.redis_port)))

    def get(self, key):
        if not self.conn:
            self.conn = yield from self._get_conn()
        return (yield from self.conn.execute('GET', key))

    def set(self, key, value, expire_time=3600):
        if not self.conn:
            self.conn = yield from self._get_conn()
        yield from self.conn.execute('SET', key, value, expire_time=expire_time)
        print("Key was created")

    def get_keys_by_pattern(self, pattern="*"):
        if not self.conn:
            self.conn = yield from self._get_conn()
        keys = yield from redis.keys(pattern)
        return keys
