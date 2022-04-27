# coding:utf-8
import yaml
import os

# 获取当前脚本所在文件夹路径
curPath = os.path.dirname(os.path.realpath(__file__))
# 获取yaml文件路径
yamlPath = os.path.join(curPath, "config.yaml")
d = yaml.load(open(yamlPath, 'r', encoding='utf-8'), Loader=yaml.FullLoader)  # 用load方法转字典
group_info = d['GroupInit']

station = d['station']
clusters = d['clusters']
clusterslist = []
for e in clusters:
    clusterslist.append(e['cluster'])

nodes = d['nodes']
nodeslist = []
for e in nodes:
    nodeslist.append(e['node'])


def get_group_info():
    ip = group_info['ip']
    port = group_info['port']
    return ip, port


def get_station():
    ip = station['ip']
    port = station['port']
    return (ip, port)


def get_cluster(id):
    if id == 0:
        return len(clusterslist)
    elif id - 1 >= len(clusterslist) or id < 0:
        raise IndexError
    return clusterslist[id - 1].copy()


def get_node(id):
    if id == 0:
        return len(nodeslist)
    elif id - 1 >= len(nodeslist) or id < 0:
        raise IndexError
    return nodeslist[id - 1].copy()


def get_data(id):
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

    return data[id - 1]
