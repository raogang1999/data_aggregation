## station 负责获取cluster的聚合数据。
## 添加cluster
## 删除cluster
## 聚合数据
## 验证签名

## 具体过程为
## 1. 初始化参数，包括 通信公钥，自己的私钥。监听，等待接入
## 2.
import decimal
import time
from queue import Queue
from threading import Thread
from typing import List

from charm.toolbox.pairinggroup import pair

from Elgamal import Elgamal
from GroupInit import GroupInit
from Message import Message
from Server import Server
from config import *
from time_to_file import save_time_to_file


class Station:

    def __init__(self, ip, port):
        self.server = Server(ip, port, "Server 启动", self.handler)
        self.group_info = GroupInit()
        self.GROUP_INIT_FLAG = True
        print("通信模块初始化成功")
        print("系统参数获取成功")
        self._to_aggregation = []
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
        # 聚合值
        self.aggregated_num = 1
        self.aggregated_deno = 1
        self.aggregated_value = []
        # 消息队列
        self.message_queue = Queue(maxsize=200)  ## 消息队列
        message_queue_thread = Thread(target=self.data_consumer)
        message_queue_thread.start()
        self.consume_info = {}

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

    def aggregation_ciphertext(self):
        agg_list = self._to_aggregation
        n = len(agg_list)
        if n < 1: return None
        aggregation_start = time.time_ns()
        num_c1, num_c2 = agg_list[0]['encrypted_numerator'][0], agg_list[0]['encrypted_numerator'][1]
        deno_c1, deno_c2 = agg_list[0]['encrypted_denominator'][0], agg_list[0]['encrypted_denominator'][1]
        for i in range(1, n):
            num_c1 *= agg_list[i]['encrypted_numerator'][0]
            num_c2 *= agg_list[i]['encrypted_numerator'][1]
            deno_c1 *= agg_list[i]['encrypted_denominator'][0]
            deno_c2 *= agg_list[i]['encrypted_denominator'][1]
        aggregation_end = time.time_ns()
        self.consume_info['aggregation_time'] = aggregation_end - aggregation_start
        return num_c1, num_c2, deno_c1, deno_c2

    def aggregation_verify(self):
        sigma_list = []
        hash_list = []
        sign_pk_list = []
        if len(self._to_aggregation) < 1:
            return True
        batch_verify_start = time.time_ns()
        for e in self._to_aggregation:
            sigma_list.append(e['sigma'])
            # 这里应该是分子分母密文的乘积
            hash_list.append(self.group_info.hash(e['encrypted_numerator'][1] * e['encrypted_denominator'][1]))
            sign_pk_list.append(self.cluster_info_map.get(e['id'])['spk'])
        sum_sigma = sigma_list[0]
        for i in range(1, len(sigma_list)):
            sum_sigma += sigma_list[i]
        left_value = pair(sum_sigma, self.group_info.get_g2())

        right_value = pair(hash_list[0], sign_pk_list[0])
        for i in range(1, len(hash_list)):
            right_value *= pair(hash_list[i], sign_pk_list[i])
        batch_verify_end = time.time_ns()
        if left_value == right_value:
            print("聚类签名验证成功")
            ## 聚类签名
            self.consume_info["batch_verify_time"] = batch_verify_end - batch_verify_start
            return True
        else:
            print("聚类签名验证失败")
            return False

    def data_consumer(self):
        flag_data_aggregated = False
        while True:
            if self.message_queue.empty() is False:
                data = self.message_queue.get()  # 收消息
                data['sigma'] = self.group_info.decode(data['sigma'])
                self._to_aggregation.append(data)
            time.sleep(0.5)

            # numerator = data["encrypted_numerator"]
            # denominator = data["encrypted_denominator"]
            # print("-------------------------------------------------------------")
            # print(data['consume_info'])
            # verify_flag_start = time.time_ns()
            # verify_flag = self.verify(sigma, numerator[1] * denominator[1],
            #                           self.cluster_info_map.get(data['id'])['spk'])
            # verify_flag_end = time.time_ns()
            # batch_verify_time = {
            #     'batch_verify_time': verify_flag_end - verify_flag_start
            # }
            # if verify_flag:
            #     nu = self.decrypt(numerator)
            #     de = self.decrypt(denominator)
            #     self.aggregated_num *= nu
            #     self.aggregated_deno *= de

    def aggregate(self):
        msg = Message()
        for e in self.cluster_info_map:
            data = self.cluster_info_map.get(e)
            ip = data['ip']
            port = data['port']
            service = "Aggregation"
            msg.set_msg(Message.CONTROL, ip, port, service, '')
            self.server.send_msg(msg)

    def handler(self, msg: dict):
        service = msg['service']

        if service == "init_group_request":
            self.init_group_request_handler(msg)
        if service == 'register_request':
            self.register_handler(msg)
        if service == "submit_data_request":
            self.message_queue.put(msg['data'])
            # data = msg['data']
            # # 处理分子分母
            # numerator = data["encrypted_numerator"]
            # denominator = data["encrypted_denominator"]
            # sigma = self.group_info.decode(data['sigma'])
            # id = data['id']
            # if self.verify(sigma, numerator[1] * denominator[1], self.cluster_info_map.get(id)['spk']):
            #     print("聚类签名验证成功")
            #     self.aggregated_num *= self.decrypt(numerator)
            #     self.aggregated_deno *= self.decrypt(denominator)
            #     print(self.aggregated_num / self.aggregated_deno)
            #
            #     print(decimal.Decimal(self.aggregated_num) / decimal.Decimal(self.aggregated_deno))
            #     # self.aggregated_m *= self.decrypt(c1_c2)
            #     # print("聚类明文为："+str(self.aggregated_m ))
            # else:
            #     print("验证失败，丢弃数据")

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
        info['ip'] = ip_c
        info['port'] = port_c
        info['spk'] = spk
        self.cluster_info_map[id] = info
        print("Gateway (" + id + ") 注册成功!")
        msg = Message()
        msg.set_msg(Message.CONTROL, ip_c, port_c, "register_response", self.self_info_to_share)
        self.server.send_msg(msg)

    # 开始聚合数据
    def start_aggregation(self, nums, duration):
        while nums > 0:
            self.aggregate()
            nums -= 1
            time.sleep(duration)
            # verify and decrypt
            # send to cluster

            verify_flag = self.aggregation_verify()
            if verify_flag:
                verify_time = {
                    "batch_verify_time": self.consume_info['batch_verify_time']
                }
                save_time_to_file("Server_batch_verify_time.txt", verify_time)
                nu_c1, nu_c2, de_c1, de_c2 = self.aggregation_ciphertext()
                self._to_aggregation = []
                decrypt_start = time.time_ns()
                aggregated_num = self.decrypt([nu_c1, nu_c2])
                aggregated_deno = self.decrypt([de_c1, de_c2])
                decrypt_end = time.time_ns()
                self.aggregated_value.append(aggregated_num / aggregated_deno)
                print(self.aggregated_value)
                decrypt_time = {
                    "server_decrypt_time": decrypt_end - decrypt_start
                }
                save_time_to_file("Server_decrypt_time.txt",decrypt_time)



if __name__ == '__main__':
    ip, port = get_station()

    sta = Station(ip, port)
    while True:
        input()
        print("开始聚类数据")
        sta.start_aggregation(9, 10)
        sta.aggregated_value = []
