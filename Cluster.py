import sys
import time
from typing import List
from multiprocessing import Queue
from threading import Thread
from Node import Node
from Message import Message
from charm.toolbox.pairinggroup import pair
from config import *

from time_to_file import save_time_to_file


# 定义簇头
class Cluster(Node):

    def __init__(self, id, ip, port):
        super().__init__(id=id, ip=ip, port=port)
        self.node_nums = 0
        self.__data_to_be_aggregation_list = []  ## 未验证的数据数据集
        self.nodes_map = {}  ## 注册的node的集合
        self.message_queue = Queue(maxsize=200)  ## 消息队列
        message_queue_thread = Thread(target=self.data_consumer)
        message_queue_thread.start()

    ## 聚类密文
    def __aggregate_encrypt(self):
        agg_list = self.__data_to_be_aggregation_list
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

    # 批验证实现
    def batch_verify(self):
        sigma_list = []
        hash_list = []
        sign_pk_list = []
        if len(self.__data_to_be_aggregation_list) < 1:
            return True
        batch_verify_start = time.time_ns()
        for e in self.__data_to_be_aggregation_list:
            sigma_list.append(e['sigma'])
            # 这里应该是分子分母密文的乘积
            hash_list.append(self.group_info.hash(e['encrypted_numerator'][1] * e['encrypted_denominator'][1]))
            sign_pk_list.append(self.nodes_map.get(e['id'])['spk'])
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
            print("批验证失败")
            return False

    # data_batch
    def data_consumer(self):
        flag_data_aggregated = False
        sleep_time = 0.1
        temp_file_name = ""
        while True:
            if self.message_queue.empty() and flag_data_aggregated:
                # verify
                # 包含分子分母
                flag = self.batch_verify()
                # send to cluster
                if flag:
                    nu_c1, nu_c2, de_c1, de_c2 = self.__aggregate_encrypt()
                    self.__data_to_be_aggregation_list = []
                    nu = [nu_c1, nu_c2]
                    de = [de_c1, de_c2]
                    numerator = self.decrypt(nu)
                    denominator = self.decrypt(de)
                    self.data_submit([numerator, denominator])
                    # 时间处理
                    batch_verify_time = {
                        'batch_verify_time': self.consume_info['batch_verify_time']
                    }
                    save_time_to_file(temp_file_name + "_batch_verify_time.txt", batch_verify_time)
                    temp_file_name = ""
                flag_data_aggregated = False
            elif self.message_queue.empty() is False:
                # 这里可以单独处理每个数据，观察数据时间
                # 批处理
                data = self.message_queue.get()  # 收消息
                data['sigma'] = self.group_info.decode(data['sigma'])
                temp_file_name += data['id']
                self.__data_to_be_aggregation_list.append(data)
                flag_data_aggregated = True
                time.sleep(sleep_time)

    def _consume_handler(self, msg):
        node_id = msg['id']
        data = msg['consume_info']
        encrypt_start = data['encrypt_start']
        encrypt_end = data['encrypt_end']
        encrypt_time = encrypt_end - encrypt_start
        signature_start = data['signature_start']
        signature_end = data['signature_end']
        signature_time = signature_end - signature_start
        report_start = data['report_start']
        report_end = data['report_end']
        report_time = report_end - report_start
        batch_verify_start = data.get("batch_verify_start", 0)
        batch_verify_end = data.get('batch_verify_end', 0)
        batch_verify_time = batch_verify_end - batch_verify_start
        return {
            'id': node_id,
            "encrypt_time": encrypt_time,
            "signature_time": signature_time,
            "report_time": report_time,
            "batch_verify_time": batch_verify_time,
        }

    ## 重写解密函数
    def decrypt(self, c: List[int]):
        self.consume_info['decrypt_start'] = time.time_ns()
        decrypt = self.el.decrypt(c[0], c[1], sk=self.self_info_to_secure['esk'])
        self.consume_info['decrypt_start'] = time.time_ns()
        return decrypt

    ## handler重写
    def submit_data_handler(self, msg):
        data = msg['data']
        # data['sigma'] = self.group_info.decode(data['sigma'])
        ## 数据生产者
        self.consume_info['report_end'] = time.time_ns()
        data['consume_info']['report_end'] = self.consume_info['report_end']
        self.message_queue.put(data)
        t = time.asctime(time.localtime(time.time()))
        print(str(t) + ": 接收到来自 (" + data['id'] + ") 的未验证的数据包。")

    # 重写 聚类handler
    def aggregation_handler(self):
        msg = Message()
        for e in self.nodes_map:
            data = self.nodes_map.get(e)
            ip = data['ip']
            port = data['port']
            service = "Aggregation"
            msg.set_msg(Message.CONTROL, ip, port, service, '')
            self.server.send_msg(msg)

    def register_request_handler(self, msg: dict):
        response = Message()
        data = msg['data']
        id = data['id']
        ip = data['ip']
        port = data['port']
        spk = data['spk']
        epk = data['epk']
        spk = self.group_info.get_group().deserialize(bytes(spk, encoding="utf-8"))
        info = {
            "ip": ip,
            "port": port,
            "spk": spk,
            "epk": epk,
        }
        self.nodes_map[id] = info
        response.set_msg(Message.CONTROL, data['ip'], data['port'], 'register_response',
                         self.self_info_to_share)
        if 'c' in id:
            print("Gateway (" + id + ") 注册成功!")
        elif 'n' in id:
            print("Device (" + id + ") 注册成功!")
        self.server.send_msg(response)
        self.node_nums = len(self.nodes_map)


if __name__ == '__main__':
    cluster_range = get_cluster(0)
    n = len(sys.argv)
    print(sys.argv)
    index = 0
    if n < 3:
        print("Usage:\t python Cluster.py id \n\t\t id <= " + str(cluster_range))
        sys.exit(-1)
    else:
        index = int(sys.argv[1])
        parent = int(sys.argv[2])
    cluster_info = get_cluster(index)
    cluster = Cluster(cluster_info['id'], cluster_info['ip'], cluster_info['port'])
    ip = ""
    port = 0
    if parent == 0:
        ip, port = get_station()
    else:
        cluster_info = get_cluster(parent)
        ip, port = cluster_info['ip'], cluster_info['port']
    cluster.register_to(ip, port)
