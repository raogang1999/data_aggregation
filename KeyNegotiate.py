from typing import List
import time
from Node import Node
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair, H
from charm.core.engine.util import objectToBytes

# class KeyManager:
#     secure = -1
#     group_info = None
#
#     def __gen_pk(self, secure: int, sk):
#         return sk ** secure
#
#     def __gen_sk(self, id: int):
#         sk = self.group_info.hash(id)
#         return sk
#
#     def __init__(self, nodelist: List[Node], group_info):
#         self.group_info = group_info
#         self.secure = self.group_info.group.random(ZR)
#         for i in range(len(nodelist)):
#             nodelist[i].sk = self.__gen_sk(nodelist[i].id)
#             nodelist[i].pk = self.__gen_pk(self.secure, nodelist[i].sk)
#
#     # 协商
#     def negotiation(self, nodelist: List[Node]):
#         n = len(nodelist)
#         # 交换公钥
#         for i in range(n):
#             for j in range(i + 1, n):
#                 nodelist[i].pkmap[nodelist[j].id] = nodelist[j].pk
#                 nodelist[j].pkmap[nodelist[i].id] = nodelist[i].pk
#         # 建立会话session
#         for i in range(n):
#             for j in range(i + 1, n):
#                 nodei_para = nodelist[i].gen_session_para()
#                 nodej_para = nodelist[j].gen_session_para()
#                 nodelist[i].save_session(nodelist[j].id, nodej_para)
#                 nodelist[j].save_session(nodelist[i].id, nodei_para)
#                 print("===node: (" + str(nodelist[i].id) + ") negotiated with node: (" + str(nodelist[j].id) + ")===")
