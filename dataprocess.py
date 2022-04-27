import matplotlib.pyplot as plt
import numpy as np


def read_from_file():
    with open("data_origin.txt", 'r') as f:
        list1 = f.readlines()
        ans = []
        for e in list1:
            ans.append(list(map(float, e.replace('\n', '').split("\t"))))
        print(ans)
    # 23, 878, 749.969583874604675072


data = [[6.35, 7.4, 7.32, 6.41, 6.51, 6.58, 6.34, 6.89, 6.57],
        [5.48, 6.56, 6.63, 5.36, 5.24, 5.63, 5.98, 5.64, 5.7],
        [7.58, 7.89, 7.78, 7.67, 7.8, 8.36, 8.56, 7.59, 7.41],
        [4.32, 5.45, 5.37, 4.42, 4.53, 4.63, 4.98, 4.12, 4.65],
        [8.32, 8.45, 8.36, 8.94, 8.52, 7.32, 8.1, 8.3, 8.95],
        [5.26, 6.31, 6.45, 5.35, 5.43, 5.96, 5.81, 5.62, 5.73],
        [10.35, 12.16, 13.32, 10.45, 10.38, 10.98, 10.45, 11.21, 10.78],
        [3.57, 4.13, 4.1, 3.66, 3.56, 3.65, 3.94, 3.74, 3.61],
        [4.23, 4.55, 4.53, 4.25, 4.36, 4.87, 4.99, 5.12, 4.83],
        [5.33, 5.69, 5.39, 5.36, 5.78, 5.64, 5.36, 5.95, 5.73]]
data = np.array(data)
mul = [1 for i in range(10)]
print(mul[0])
for i in range(9):
    for e in data[:, i:i + 1]:
        mul[i] *= e[0]

print(mul)
data = [41542482.8237966, 144711292.4859077, 145787246.33627856, 48538108.58633108, 51928548.54341418,
        68862402.02603032, 83759205.3043307, 72396216.0242833, 71271641.08165805]
x = [i for i in range(9)]
data1 = [pow(i, 0.1) for i in data]



