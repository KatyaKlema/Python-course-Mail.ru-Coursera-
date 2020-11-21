import asyncio


class MetricsStorage:
    """ class for storing all server metrics """
    def __init__(self):
        self.__metrics_dict = {}

    def put(self, key, value, timestamp):
        if not (key in self.__metrics_dict.keys()):
            self.__metrics_dict[key] = {}
        self.__metrics_dict[key][timestamp] = value

    def get(self, key):
        tmp_data = self.__metrics_dict
        if key != '*':
            tmp_data = {
                key: tmp_data.get(key, {})
            }
        result = {}
        for key, timestamp in tmp_data.items():
            result[key] = sorted(timestamp.items())
        return result


class ReadError(ValueError):
    pass


class Parser:
    """ class for encoding and decoding messages """

    def decode(self, responses):
        """ decode server response """
        msgs = []
        for res in responses:
            if res:
                for key, timestamp_dict in res.items():
                    for timestamp, value in timestamp_dict:
                        msgs.append("{} {} {}".format(key, value, timestamp))
        ret_msg = 'ok\n'
        if len(msgs) > 0:
            ret_msg += '\n'.join(msgs) + '\n'
        ret_msg += '\n'
        return ret_msg

    def encode(self, req):
        """ encode client request for server"""
        try:
            parts = req.split('\n')
            parts = list([part for part in parts if len(part) > 0])
            if len(parts) == 0:
                raise ValueError('error: invalid method')
        except ValueError:
            raise ReadError('wrong command')


        cmds = []
        for part in parts:
            try:
                method, params = part.strip().split(" ", 1)
                if method == 'put':
                    if len(params.split(' ')) != 3:
                        raise ValueError('error: invalid method')
                    key, value, timestamp = params.split(' ')
                    if key.isnumeric():
                        raise ValueError('error: invalid method')
                    cmds.append((method, key, float(value), int(timestamp)))
                elif method == 'get':
                    if len(params.split(' ')) != 1:
                        raise ValueError('error: invalid method')
                    key = params
                    if key.isnumeric():
                        raise ValueError('error: invalid method')
                    cmds.append((method, key))
                else:
                    raise ValueError('error: invalid method')
            except ValueError:
                raise ReadError('wrong command')
        return cmds


class ExecuteError(Exception):
    pass


class Executor:
    """ class for running server methods"""
    def __init__(self, metrics_storage):
        self.metrics_storage = metrics_storage

    def run(self, method, *params):
        if method == 'put':
            return self.metrics_storage.put(*params)
        elif method == 'get':
            return self.metrics_storage.get(*params)
        else:
            raise ExecuteError('invalid method')


class ClientServerProtocol(asyncio.Protocol):
    """ server class """
    metrics_storage = MetricsStorage()

    def __init__(self):
        super().__init__()

        self.parser = Parser()
        self.executor = Executor(self.metrics_storage)
        self.buffer = b''

    def process_data(self, req):
        """ process input server commands"""
        cmds = self.parser.encode(req)
        responses = []
        for cmd in cmds:
            res = self.executor.run(*cmd)
            responses.append(res)
        return self.parser.decode(responses)

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, req):
        """ this method is running when request from sockets are received """
        self.buffer += req
        try:
            decoded_req = self.buffer.decode()
        except UnicodeError:
            return

        # wait data until get \n at the end of the request
        if not decoded_req.endswith('\n'):
            return

        self.buffer = b''

        try:
            res = self.process_data(decoded_req)
        except(ReadError, ExecuteError) as e:
            self.transport.write('error\n{}\n\n'.format(e).encode())
            return
        self.transport.write(res.encode())


def run_server(host, port):
    loop = asyncio.get_event_loop()
    coro = loop.create_server(
        ClientServerProtocol,
        host, port
    )
    server = loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

