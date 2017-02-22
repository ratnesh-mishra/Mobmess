import asyncio
import hashlib
from datetime import datetime
import json
from asyncio import coroutine


class ServerManager:
    def __init__(self, client_session, redis_manager):
        self.client_session = client_session
        self.redis_manager = redis_manager


    @coroutine
    def detect_duplicate(self, message, dest_user, source_user):
        """
        Improvements can be made
        :param message:
        :param dest_user:
        :param source_user:
        :return True or False:
        """
        now_time = int(datetime.now().strftime("%s"))
        keys = []
        message = json.dumps(message)
        for i in range(1, 5):
            tt = str(now_time - i)
            key_form = "{}:{}:{}:{}".format(message, dest_user, source_user, tt)
            keys.append(hashlib.sha512(key_form.encode()).hexdigest())
        get_key = yield from self.redis_manager.get_keys(*keys)
        return False if get_key else True

    def send_message(self, message, dest_add, dest_user, source_user):
        try:
            """ Check for collision from redis"""
            message = json.dumps(message)
            if (yield from self.detect_duplicate(message, dest_user, source_user)):
                """ If collision don't send """
                raise Exception("Duplicate message")
            now_time = int(datetime.now().strftime("%s"))
            key = "{}:{}:{}:{}".format(message, dest_user, source_user, now_time)

            resp, res = yield from asyncio.gather(asyncio.wait_for(self.client_session.request('post', "{}:{}".format(dest_add[0], dest_add[1]),
                                                  params={"message": message}), timeout=5),
                                                  self.redis_manager.set(key, message))
            if resp.status == 200:
                return {"result": "Message delivered"}
            else:
                raise Exception("error Occured")
        except Exception as e:
            return str(e)


