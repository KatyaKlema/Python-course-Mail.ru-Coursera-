import socket
import time
import functools


def compare(item1, item2):
    if item1[0] < item2[0]:
        return 1
    elif item1[0] > item2[0]:
        return -1
    else:
        return 0


class ClientError(Exception):
    pass


def compare(item1, item2):
    if item1[0] < item2[0]:
        return -1
    elif item1[0] > item2[0]:
        return 1
    else:
        return 0


class Client:
    def __init__(self, host, port, timeout=None):
        try:
            self.sock = socket.create_connection((host, port))
        except socket.error as err:
            raise ClientError()

    def put(self, metric, value, timestamp=None):
        if timestamp is None:
            timestamp = int(time.time())
        try:
            # send data to server
            msg = 'put ' + metric + ' ' + str(value) + ' ' + str(timestamp) + '\n'
            self.sock.sendall(msg.encode())
            res = self.sock.recv(1024)
            res = res.decode()
            if res != 'ok\n\n':
                raise ClientError()
        except socket.error:
            raise ClientError()

    def get(self, metric):
        try:
            # get data from server
            msg = 'get ' + metric + '\n'
            self.sock.sendall(msg.encode())
        except socket.error:
            raise ClientError()
        res = b''
        # accumulate buffer res
        while not res.endswith(b"\n\n"):
            try:
                res += self.sock.recv(1024)
            except socket.error as err:
                raise ClientError()
        res = res.decode()
        ans_dict = {}
        if isinstance(res, Exception) or res == 'error\nwrong command\n\n':
            raise ClientError()
        elif res == 'ok\n\n':
            return ans_dict

        results = list(res.split('\n'))
        if len(results) == 0 or results[0] != 'ok':
            raise ClientError()
        results = results[1: len(results) - 2]
        try:
            for result in results:
                key_metric = ''
                i = 0
                while i < len(result) and result[i] != ' ':
                    key_metric += result[i]
                    i += 1
                if key_metric == '':
                    raise ClientError()
                i += 1
                metric_value = ''
                while i < len(result) and result[i] != ' ':
                    metric_value += result[i]
                    i += 1
                i += 1
                if metric_value == '':
                    raise ClientError()
                timestamp = ''
                while i < len(result) and result[i] != ' ':
                    timestamp += result[i]
                    i += 1
                if timestamp == '':
                    raise ClientError()
                try:
                    timestamp = int(timestamp)
                    metric_value = float(metric_value)
                except ValueError:
                    raise ClientError()
                if key_metric in ans_dict.keys():
                    ans_dict[key_metric].append((timestamp, metric_value))
                else:
                    ans_dict[key_metric] = [(timestamp, metric_value)]
                ans_dict[key_metric].sort(key=functools.cmp_to_key(compare))
            if len(ans_dict) == 0:
                raise ClientError()
            return ans_dict
        except ClientError:
            raise ClientError()

    def __del__(self):
        self.sock.close()

# client = Client("127.0.0.1", 8888, timeout=15)
# client.put(metric='palm.cpu', value=0.5, timestamp=1150864247)
