import sys
import time
from typing import List
from multiprocessing import Queue
from threading import Thread
from Node import Node
from Message import Message
from charm.toolbox.pairinggroup import pair
from config import *


# 定义簇头
class Cluster(Node):

    def __init__(self, id, ip, port):
        super().__init__(id=id, ip=ip, port=port)
        self.__batch_verify_flag = False  # 批验证情况
        self.__data_to_be_aggregation_list = []  ## 未验证的数据数据集
        self.nodes_map = {}  ## 注册的node的集合
        self.message_queue = Queue(maxsize=200)  ## 消息队列
        message_queue_thread = Thread(target=self.data_consumer)
        message_queue_thread.start()
        print("Cluster Init Success")

    ## 聚类密文
    def __aggregate_encrypt(self):
        agg_list = self.__data_to_be_aggregation_list
        n = len(agg_list)
        c1, c2 = agg_list[0]['encrypted'][0], agg_list[0]['encrypted'][1]
        for i in range(1, n):
            c1 *= agg_list[i]['encrypted'][0]
            c2 *= agg_list[i]['encrypted'][1]
        return c1, c2

    # 批验证实现
    def batch_verify(self):
        sigma_list = []
        hash_list = []
        sign_pk_list = []
        if len(self.__data_to_be_aggregation_list) < 1:
            return True
        for e in self.__data_to_be_aggregation_list:
            sigma_list.append(e['sigma'])
            hash_list.append(self.group_info.hash(e['encrypted'][1]))
            sign_pk_list.append(self.nodes_map.get(e['id'])['spk'])
        sum_sigma = sigma_list[0]
        for i in range(1, len(sigma_list)):
            sum_sigma += sigma_list[i]
        left_value = pair(sum_sigma, self.group_info.get_g2())

        right_value = pair(hash_list[0], sign_pk_list[0])
        for i in range(1, len(hash_list)):
            right_value *= pair(hash_list[i], sign_pk_list[i])
        if left_value == right_value:
            print("批验证成功")
            ## 聚类签名
            batch_verify_info = {}
            # batch_verify_info['timestamp'] = int(time.time())
            # batch_verify_info['sigma'] = sum_sigma
            # batch_verify_info['hash_list'] = hash_list
            c1, c2 = self.__aggregate_encrypt()
            batch_verify_info['encrypted'] = [c1, c2]
            ## 聚合后清空原来的数据
            self.__data_to_be_aggregation_list = []
            self.__batch_verify_flag = True
            return batch_verify_info['encrypted']
        else:
            self.__batch_verify_flag = False
            print("批验证失败")
            return False

    # data_batch
    def data_consumer(self):
        flag_data_aggregated = False
        sleep_time = 1
        while True:
            alpha = 200 / (self.message_queue.qsize() + 1)
            if alpha > 20:
                sleep_time = 0.8
            elif alpha > 10:
                sleep_time = 0.5
            elif alpha > 4:
                sleep_time = 0.2
            elif alpha <= 1.5:
                sleep_time = 0

            if self.message_queue.empty() and flag_data_aggregated:
                # verify
                data = self.batch_verify()
                # send to cluster
                if data:
                    m = self.decrypt(data)
                    self.data_submit(m)
                flag_data_aggregated = False
            else:
                # 批处理
                data = self.message_queue.get()  # 收消息
                data['sigma'] = self.group_info.decode(data['sigma'])
                self.__data_to_be_aggregation_list.append(data)
                time.sleep(sleep_time)
                flag_data_aggregated = True

    ## 重写解密函数
    def decrypt(self, c: List[int]):
        return self.el.decrypt(c[0], c[1], sk=self.self_info_to_secure['esk'])

    ## handler重写
    def submit_data_handler(self, msg):
        data = msg['data']
        # data['sigma'] = self.group_info.decode(data['sigma'])
        ## 数据生产者
        self.message_queue.put(data)
        t = time.asctime(time.localtime(time.time()))
        print(str(t) + ": received a package without verify from (" + data['id'] + ") ")

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
        print(id + ": is registered !")
        self.server.send_msg(response)


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
