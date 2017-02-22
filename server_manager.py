import asyncio


class ServerManager:
    def __init__(self, client_session, redis_manager):
        self.client_session = client_session
        self.redis_manager = redis_manager

    def send_message(self, message, dest_add):
        try:
            """ Check for collision
             Check from redis"""

            resp = asyncio.wait_for(self.client_session.request('post', "{}:{}".format(dest_add[0], dest_add[1]),
                                    params={"message": message}), timeout=5)
            if resp.status == 200:
                return {"result": "success"}

            else:
                return "error Occured"
        except Exception as e:
            return str(e)


