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
