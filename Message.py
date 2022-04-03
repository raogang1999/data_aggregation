# 定义传输消息的格式
import json
import pickle
import socket
from enum import Enum


class Message:
    CONTROL = 1
    DATA = 2

    def __init__(self):
        self.msg = {}

    def set_msg(self, type: int, ip: str, port: int, service: str, data):
        self.msg = {
            'type': type,
            'ip': ip,
            'port': port,
            'service': service,
            'data': data
        }

    def get_ip(self):
        return self.msg['ip']

    def get_port(self):
        return self.msg['port']

    def get_msg(self):
        return self.msg

    def set_data(self, data):
        self.msg['data'] = data


if __name__ == '__main__':
    Message()
