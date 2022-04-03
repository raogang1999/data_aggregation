from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair, H
from charm.core.engine.util import objectToBytes

from Server import Server
from config import *

from Message import Message


class GroupInit:

    def hash(self, m):
        c = objectToBytes(m, self.get_group())
        digist = self.get_group().hash(c, G1)
        return digist

    def get_group(self):
        return self.__group

    def set_g1(self, g1):
        self.__g1 = g1

    def set_g2(self, g2):
        self.__g2 = g2

    def get_g1(self):
        return self.__g1

    def get_g2(self):
        return self.__g2

    def decode(self, x):
        return self.get_group().deserialize(bytes(x, encoding="utf-8"))

    def __init__(self):
        self.__group = PairingGroup('SS512')
        self.__g1 = self.get_group().random(G1)
        self.__g2 = self.get_group().random(G2)
