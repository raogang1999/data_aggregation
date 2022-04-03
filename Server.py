import json
import socket
import threading
from copy import copy

from Encoder import Decoder, Encoder


class Server:
    def received_msg(self, handler):
        while True:
            received_data = self.udp_socket.recvfrom(2048)
            msg = json.loads(received_data[0])
            handler(msg)

    def send_msg(self, msg):
        a = self.ip
        temp_msg = copy(msg)
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = json.dumps(temp_msg.get_msg(), cls=Encoder)
        client.sendto(data.encode('utf-8'), (msg.get_ip(), msg.get_port()))

    def __init__(self, ip, port, greet, handler):
        self.ip = ip
        self.port = port
        # 1.创建套接字
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 2.绑定本地的信息
        self.udp_socket.bind(((ip, port)))
        th = threading.Thread(target=self.received_msg, args=[handler])
        th.start()
        print("----- information-----")
        print(greet)
        print("ip: " + ip)
        print("port: " + str(port))
