# 继承原有的JSONEncoder类
import json
from typing import Callable, Any

from charm.core.math.pairing import pc_element
from charm.toolbox.pairinggroup import PairingGroup, serialize


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PairingGroup):
            b = serialize(obj)
            s = str(b, encoding='utf-8')
            return s
        if isinstance(obj, pc_element):
            b = serialize(obj)
            s = str(b, encoding="utf-8")
            return s
        # if isinstance(obj, gmpy2.mpz):
        #     return obj.__str__()
        super(Encoder, self).default(obj)


class Decoder(json.JSONDecoder):
    def decode(self, s: str, _w: Callable[..., Any] = ...) -> Any:
        pass
