from vyked import HTTPService, get, post, Host
from .utils import *
from asyncio import coroutine
from aiohttp import ClientSession, request
from aiohttp.web import Request, Response
import random
import string
import asyncio
from functools import partial
from .server_manager import ServerManager
from .redis_manager import RedisManager
con_key_pattern = "mobile_clients"
keys_pattern = con_key_pattern+"*"
config = json_file_to_dict('config.json')


class MobileServer(HTTPService):
    def __init__(self, name, version, host, port, server_manager, redis_manager):
        """
        For supporting multiple servers might have to use distributed source maybe redis
        """
        self.available_hosts = dict()
        self.server_manager = server_manager
        self.redis_manager = redis_manager
        super(MobileServer, self).__init__(name, version, host, port, allow_cross_domain=True)

    def check_in_available_hosts(self, host):
        host_key = con_key_pattern+":"+str(tuple(host))
        available_hosts = yield from self.redis_manager.get_keys_by_pattern(keys_pattern)
        if host_key in available_hosts:
            return True
        return False


    @staticmethod
    def get_random_name():
        """
        :return:Random usernames to users
        """
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(6))

    def return_response(self, status, content_type, body):
        return Response(status=status, body=body, content_type=content_type)

    create_success_response = partial(return_response, status=200, content_type='application/json')
    create_server_error_response = partial(return_response, status=500, content_type='application/json')

    @coroutine
    @get(path='/connect')
    def get_connection(self, _request: Request):
        peername = _request.transport.get_extra_info('peername')
        if peername is not None:
            user_address = peername
        username = _request.GET.get('username', MobileServer.get_random_name())
        """ Get Keys from redis and check if present """
        # available_hosts = yield from self.redis_manager.get_keys_by_pattern(keys_pattern)
        mobile_format_key = con_key_pattern+":"+str(tuple(user_address))
        if self.check_in_available_hosts(peername):
            return self.create_success_response(json.dumps({"message": "Relax Dude we have already got you hooked"}).encode())
        else:
            yield from redis_manager.set(mobile_format_key, username)
        return self.create_success_response(json.dumps({"message": "On board mate"}).encode())

    @coroutine
    @get('/available-buddies')
    def get_available_users(self, request:Request):
        # hosts = json.dumps(self.available_hosts.keys())
        available_hosts = yield from self.redis_manager.get_keys_by_pattern(keys_pattern)
        hosts = json.dumps(available_hosts)
        return self.create_success_response(hosts)

    @coroutine
    @post(path='/receive')
    def receive_message(self, _request: Request):
        peername = _request.transport.get_extra_info('peername')
        payload = yield from _request.post()
        try:
            if self.check_in_available_hosts(tuple(peername)):
                message = payload.get('message', '')
                _to = payload.get('to')
                _from = payload.get('from')
                flag = False
                for users in self.redis_manager.get_keys_by_pattern(con_key_pattern):
                    if users.value == _to:
                        dest_add = users.key
                        flag = True
                if flag:
                    dest = get_dest_from_key(dest_add)
                    resp = yield from self.server_manager.send_message(message, _to, _from, dest)
                    if resp:
                        return self.create_success_response("Message delivered dude".encode())
                else:
                    raise Exception("User is not available")
        except Exception as e:
            return self.create_server_error_response(json.dumps(str(e)).encode())


if __name__ == "__main__":
    client_session = ClientSession()
    redis_manager = RedisManager(config['REDIS_HOST'], config['REDIS_PORT'])
    server_manager = ServerManager(client_session, redis_manager)
    http_service = MobileServer(config['service_name'], config['version'], config['host'], config['port'],
                                server_manager, redis_manager)
    # loop = asyncio.get_event_loop()
    # loop.run_forever(server_manager.poll_connections())
    http_service.clients = []
    Host.registry_host = config['REGISTRY_HOST']
    Host.registry_port = config['REGISTRY_PORT']
    Host.pubsub_host = config['REDIS_HOST']
    Host.pubsub_port = config['REDIS_PORT']
    Host.name = config['service_name']
    Host.attach_service(http_service)
    Host.run()










