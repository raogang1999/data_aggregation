import random

import gmpy2
from pyunit_prime import get_large_prime_length, get_large_prime_bit_size


class Elgamal:

    def __init__(self):
        self.p = 84168723813333528916606332677013585264716784583392212245101661795038739237643
        self.q = 707869247888833

    def random(self):
        return random.randint(100, self.q)

    def ken_gen(self):
        sk = random.randint(100, self.q)
        g = random.randint(100000000000, self.q)
        pk = gmpy2.powmod(g, sk, self.p)

        return (int(pk), int(sk), int(g), int(self.p))

    def encrypt(self, m, g, pk):
        r = random.randint(100, self.q)
        c1 = gmpy2.powmod(g, r, self.p)
        c2 = m * gmpy2.powmod(pk, r, self.p) % self.p
        return int(c1), int(c2)

    def decrypt(self, c1, c2, sk):
        c1_inv = gmpy2.invert(gmpy2.powmod(c1, sk, self.p), self.p)
        return c2 * c1_inv % self.p

    def mul(self, c1, c2, c3, c4):
        return int(c1 * c3 % self.p), int(c2 * c4 % self.p)


if __name__ == '__main__':
    el = Elgamal()
    m1 = 9991
    (pk, sk, g, p) = el.ken_gen()
    c1, c2 = el.encrypt(m1, g, pk)
    d = el.decrypt(c1, c2, sk)
    print(d)
    m2 = 5432432
    c3, c4 = el.encrypt(m2, g, pk)
    d = el.decrypt(c3, c4, sk)
    print(d)
    c5, c6 = el.mul(c1, c2, c3, c4)
    d = el.decrypt(c5, c6, sk)
    print(d)
