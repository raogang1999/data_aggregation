from typing import List

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties  # 步骤一

base = 4086094


verify_batch = [8022119, 8172188, 16340945, 28601178, 29718534, 30821027, 31635402, 32944515, 32557152, 33160996]
verify_one_by_one = [8172188, 16279108, 24385050, 37183122, 48952512, 57147986, 70358393, 78662109, 90520056, 98952240]
decrypt_batch = [31443, 29965, 31792, 31416, 32209, 34650, 30477, 29293, 29088, 28853]
decrypt_one_by_one = [31990, 64716, 96706, 128525, 159459, 191816, 224032, 254834, 284977, 315551]
device = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def format_data(data: List[int], scale):
    for i in range(len(data)):
        data[i] = data[i] * 10 ** (-1 * scale)


format_data(verify_batch, 6)
format_data(verify_one_by_one, 6)
format_data(decrypt_batch, 3)
format_data(decrypt_one_by_one, 3)


# ...
def verify_plt(batch, on_by_one):
    font = FontProperties(fname=r"simsun.ttc", size=12)  # 步骤二

    plt.plot(device, on_by_one, color="red", )
    plt.plot(device, batch, color="green", )

    # plt.xlim(0, 10)  # 设置x轴范围
    # plt.ylim(0, 10)  # 设置y轴范围
    # 刻度
    x_ticks = np.linspace(1, 10, 10)
    plt.xticks(x_ticks)
    # 刻度
    y_ticks = np.linspace(10, 100, 10)
    plt.yticks(y_ticks)
    plt.ylabel('时间消耗（单位：毫秒）', fontproperties=font)  # 设置x轴标签
    plt.xlabel('Device数量（单位：个）', fontproperties=font)  # 设置y轴标签
    plt.title("签名验证时间消耗对比", fontproperties=font)
    plt.legend(["单独验证", "聚类验证"], prop=font)
    plt.grid()
    plt.savefig("verify_plt.jpg")
    plt.show()



def decrypt_plt(batch, on_by_one):
    font = FontProperties(fname=r"simsun.ttc", size=12)  # 步骤二

    plt.plot(device, on_by_one, color="red", )
    plt.plot(device, batch, color="green", )

    # plt.xlim(0, 10)  # 设置x轴范围
    # plt.ylim(0, 10)  # 设置y轴范围
    # 刻度
    x_ticks = np.linspace(1, 10, 10)
    plt.xticks(x_ticks)
    # 刻度
    y_ticks = np.linspace(20, 320,11)
    plt.yticks(y_ticks)
    plt.ylabel('时间消耗（单位：微秒）', fontproperties=font)  # 设置x轴标签
    plt.xlabel('Device数量（单位：个）', fontproperties=font)  # 设置y轴标签
    plt.title("解密时间消耗对比", fontproperties=font)
    plt.legend(["单独解密", "聚类解密"], prop=font)
    plt.grid()
    plt.savefig("decrypt_plt.jpg")
    plt.show()

def means_plt():
    data = [41542482.8237966, 144711292.4859077, 145787246.33627856, 48538108.58633108, 51928548.54341418,
            68862402.02603032, 83759205.3043307, 72396216.0242833, 71271641.08165805]
    x = [str(i)+"" for i in  range(1,10)]

    data1 = [pow(i, 0.1) for i in data]
    font = FontProperties(fname=r"simsun.ttc", size=12)  # 步骤二
    plt.plot(x,data1, color="green")
    plt.ylabel('平均值（单位：度）', fontproperties=font)  # 设置x轴标签
    plt.xlabel('日期', fontproperties=font)
    y_ticks = np.linspace(5.5, 7, 7)
    plt.yticks(y_ticks)
    plt.legend(['平均值'],prop=font)
    plt.title("用户电量消耗平均值", fontproperties=font)
    plt.grid()
    plt.savefig("means_plt.jpg")
    plt.show()

verify_plt(verify_batch, verify_one_by_one)
decrypt_plt(decrypt_batch, decrypt_one_by_one)
means_plt()

