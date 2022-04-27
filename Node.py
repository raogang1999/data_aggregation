import sys
import time
from fractions import Fraction
from typing import List

from charm.toolbox.pairinggroup import ZR, pair

from Elgamal import Elgamal
from GroupInit import GroupInit
from Message import Message
from Server import Server
from config import *


# 记得导入所需的模块

class Node:
    REG_FLAG = False
    __other_node_info = []
    __data__list = []

    def handler(self, msg: dict):
        service = msg['service']
        if service == 'register_response':
            self.register_response_handler(msg)
        if service == 'init_group_response':
            self.init_group_response_handler(msg)
        if service == 'register_request':
            self.register_request_handler(msg)
        if service == "submit_data_request":
            self.submit_data_handler(msg)
        if service == "Aggregation":
            self.aggregation_handler()

    def get_port(self):
        return self.self_info_to_share['port']

    def get_ip(self):
        return self.self_info_to_share["ip"]

    def get_id(self):
        return self.self_info_to_share['id']

    def __init__(self, id, ip, port):
        self.GROUP_INIT_FLAG = False
        self.submit_obj_info = {}  # 提交对象的信息
        self.self_info_to_share = {}
        self.self_info_to_secure = {}
        if 'c' in id:
            self.GREET = "Gateway: (" + id + ") 已启动!"
        else:
            self.GREET = "Device: (" + id + ") 已启动!"

        self.server = Server(ip, port, self.GREET, handler=self.handler)
        print("通信模块初始化成功")
        # 签名和加密分别有sk，pk
        self.el = Elgamal()
        # self.group_info = GroupInit()
        self.group_info = GroupInit()

        msg = Message()
        while not self.GROUP_INIT_FLAG:
            ip1, port1 = get_station()
            data = {
                'ip': ip,
                'port': port,
            }
            msg.set_msg(Message.CONTROL, ip1, port1, "init_group_request", data)
            self.server.send_msg(msg)
            time.sleep(1)
        print("系统参数获取成功")
        # 签名私钥
        self.__x = self.group_info.get_group().random(ZR)
        (pk, sk, g, p) = self.el.ken_gen()
        # 私有属性初始化
        self.self_info_to_secure['epk'] = (pk, g)
        self.self_info_to_secure['esk'] = sk
        self.self_info_to_secure['spk'] = self.group_info.get_g2() ** self.__x
        self.self_info_to_secure['ssk'] = self.__x
        # 公开共享
        self.self_info_to_share['id'] = id
        self.self_info_to_share['ip'] = ip
        self.self_info_to_share['port'] = port
        self.self_info_to_share['spk'] = self.group_info.get_g2() ** self.__x
        self.self_info_to_share['epk'] = self.self_info_to_secure['epk']
        # self.pkmap = {}  # 邻居节点的公钥
        # self.session = {}  # 邻居节点的会话session
        # self.u = self.group_info.group.random(ZR)
        self.consume_info = {}
        self.__data__list = []

    # def gen_session_para(self):
    #     self.r = self.group_info.group.random(ZR)
    #     para = self.pk ** self.r
    #     return para

    # 保存会话密钥
    # def save_session(self, other_node_id, session_para):
    #     self.session[other_node_id] = pair(self.sk, session_para * self.pkmap[other_node_id] ** self.r)
    # 混合数据
    def node_data_mix(self):
        pass

    ## 发送节点数据给簇头
    def data_submit(self, data: List[int]):
        if self.REG_FLAG == False:
            print("请先完成注册")
        else:
            msg = Message()
            # data是浮点数由分子分母组成
            num_c1, num_c2 = self.encrypt(data[0])
            deno_c1, deno_c2 = self.encrypt(data[1])
            data = {}
            data['id'] = self.get_id()
            data['encrypted_numerator'] = [num_c1, num_c2]
            data['encrypted_denominator'] = [deno_c1, deno_c2]
            sigma = self.signature(num_c2 * deno_c2)
            data['sigma'] = sigma
            self.consume_info['report_start'] = time.time_ns()
            data['consume_info'] = self.consume_info
            msg.set_msg(Message.DATA, self.submit_obj_info['ip'], self.submit_obj_info['port'], "submit_data_request",
                        data)
            print("密文签名完成，上报数据。")
            self.server.send_msg(msg)

    ## 使用簇头节点的公钥加密数据
    def encrypt(self, data):
        encrypt_start = time.time_ns()
        encrypt = self.el.encrypt(data, g=self.submit_obj_info['epk'][1], pk=self.submit_obj_info["epk"][0])
        encrypt_end = time.time_ns()
        self.consume_info["encrypt_time"] = encrypt_end - encrypt_start
        return encrypt

    ## 解密数据
    def decrypt(self, c):
        raise NotImplementedError

    # 签名 u = c2,签名和加密分别有sk，pk
    def signature(self, c2):
        # 时间戳
        signature_start = time.time_ns()
        sigma = self.group_info.hash(c2) ** self.self_info_to_secure['ssk']
        signature_end = time.time_ns()
        self.consume_info['signature_time'] = signature_end - signature_start
        return sigma

    #
    def load_data(self, data: List[float]):
        data.reverse()
        self.__data__list = data + self.__data__list

    # 注册响应回调函数
    def register_response_handler(self, msg):
        self.REG_FLAG = True
        data = msg['data']
        self.submit_obj_info = data
        if self.submit_obj_info.get('spk') is not None:
            self.submit_obj_info['spk'] = self.group_info.get_group().deserialize(
                bytes(self.submit_obj_info['spk'], encoding="utf-8"))
        print("注册成功：（" + data['ip'] + "," + str(data['port']) + ")")

        # 向上级注册

    def register_request_handler(self, msg):
        raise NotImplementedError

    def submit_data_handler(self, msg):
        raise NotImplementedError

    def init_group_response_handler(self, msg):
        data = msg['data']
        self.group_info.set_g1(self.group_info.decode(data['g1']))
        self.group_info.set_g2(self.group_info.decode(data['g2']))
        self.GROUP_INIT_FLAG = True

    def aggregation_handler(self):
        if len(self.__data__list) > 0:
            data = self.__data__list.pop()
            ## m是一个浮点数
            temp = Fraction(data).limit_denominator()
            # 分子
            numerator = temp.numerator
            # 分母
            denominator = temp.denominator
            self.data_submit([numerator, denominator])

    def register_to(self, ip, port):
        msg = Message()
        msg.set_msg(Message.CONTROL, ip, port, service="register_request", data=self.self_info_to_share)
        self.server.send_msg(msg)

    def verify(self, sigma, c2, pk) -> bool:
        verify_start = time.time_ns()
        temp1 = pair(sigma, self.group_info.get_g2())
        temp2 = pair(self.group_info.hash(c2), pk)
        verify_end = time.time_ns()
        self.consume_info['verify_time'] = verify_end - verify_start
        return temp2 == temp1


def main():
    cluster_range = get_node(0)
    n = len(sys.argv)
    index = 0
    parent = 0
    if n < 3:
        print("Usage:\t python Cluster.py id parent\n\t\t id <= " + str(cluster_range))
        sys.exit(-1)
    else:
        index = int(sys.argv[1])
        parent = int(sys.argv[2])
    node_info = get_node(index)
    data = get_data(index)
    node = Node(node_info['id'], node_info['ip'], node_info['port'])
    cl = get_cluster(parent)  # 默认为1
    node.register_to(cl['ip'], cl['port'])
    node.load_data(data)


if __name__ == '__main__':
    # test()
    main()
