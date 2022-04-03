## station 负责获取cluster的聚合数据。
## 添加cluster
## 删除cluster
## 聚合数据
## 验证签名

## 具体过程为
## 1. 初始化参数，包括 通信公钥，自己的私钥。监听，等待接入
## 2.
import json
import time
from copy import copy
import socket
from typing import List

from Server import Server
from GroupInit import GroupInit
from config import *
from Message import Message
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair, H
from Elgamal import Elgamal


class Station:
    def __init__(self, ip, port):
        self.server = Server(ip, port, "Station start", self.handler)
        self.group_info = GroupInit()
        self.GROUP_INIT_FLAG = True
        print("Group init success")
        ## 密钥初始
        self.self_info_to_share = {}
        self.self_info_to_secure = {}
        self.el = Elgamal()
        (pk, sk, g, p) = self.el.ken_gen()
        # 私有属性初始化
        self.self_info_to_secure['epk'] = (pk, g)
        self.self_info_to_secure['esk'] = sk
        # 公开共享
        # self.self_info_to_share['id'] = id
        self.self_info_to_share['ip'] = ip
        self.self_info_to_share['port'] = port
        self.self_info_to_share['epk'] = self.self_info_to_secure['epk']
        ## 簇头列表
        self.cluster_info_map = {}

    def init_group_request_handler(self, msg):
        response = Message()
        data = msg['data']
        ip = data['ip']
        port = data['port']
        group = {}
        group['g1'] = self.group_info.get_g1()
        group['g2'] = self.group_info.get_g2()
        response.set_msg(Message.CONTROL, ip, port, 'init_group_response', group)
        self.server.send_msg(response)

    def handler(self, msg: dict):
        service = msg['service']

        if service == "init_group_request":
            self.init_group_request_handler(msg)
        if service == 'register_request':
            self.register_handler(msg)
        if service == "submit_data_request":
            data = msg['data']
            c1_c2 = data["encrypted"]
            sigma = self.group_info.decode(data['sigma'])
            id = data['id']
            if self.verify(sigma, c1_c2[1], self.cluster_info_map.get(id)['spk']):
                print("验证成功")
                m = self.decrypt(c1_c2)
                print(m)
            else:
                print("验证失败，丢弃数据")

    def decrypt(self, c: List[int]):
        return self.el.decrypt(c[0], c[1], self.self_info_to_secure['esk'])

    ## 验证与解密
    def verify(self, sigma, c2, pk):
        temp1 = pair(sigma, self.group_info.get_g2())
        temp2 = pair(self.group_info.hash(c2), pk)
        return temp2 == temp1
        pass

    ## 通信函数

    # 注册处理器，收到簇头的注册请求，保存注册信息，返回station的加密公钥
    def register_handler(self, msg: dict):
        data = msg['data']
        id = data['id']
        ip_c = data['ip']
        port_c = data['port']
        spk = self.group_info.decode(data['spk'])
        info = {}
        ip, port = get_station()
        info['ip'] = ip
        info['port'] = port
        info['spk'] = spk
        self.cluster_info_map[id] = info
        print("cluster (" + id + ") is registered successfully!")
        msg = Message()
        msg.set_msg(Message.CONTROL, ip_c, port_c, "register_response", self.self_info_to_share)
        self.server.send_msg(msg)


if __name__ == '__main__':
    ip, port = get_station()

    sta = Station(ip, port)
