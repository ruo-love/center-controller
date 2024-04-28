from pymongo import MongoClient


def connect():
    # 创建MongoDB客户端对象
    client = MongoClient('localhost', 27017)  # 默认连接到本地主机的27017端口

    # 获取数据库实例
    db = client['facebook']

    return db
