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

    def get_keys(self, keys):
        if not self.conn:
            self.conn = yield from self._get_conn()
        if isinstance(keys, list):
            return [(yield from self.conn.execute('GET', key)) for key in keys]
        else:
            return (yield from self.conn.execute('GET', keys))

    def set(self, key, value, expire_time=3600):
        if not self.conn:
            self.conn = yield from self._get_conn()
        return (yield from self.conn.execute('SET', key, value, expire_time=expire_time))

    """ See if we can club multiple client keys in hash store """
    def get_keys_by_pattern(self, pattern="*"):
        if not self.conn:
            self.conn = yield from self._get_conn()
        keys = yield from redis.keys(pattern)
        return keys


