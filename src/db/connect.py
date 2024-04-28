from pymongo import MongoClient


def connect():
    # 创建MongoDB客户端对象
    client = MongoClient('mongodb://centerController:715625zl..@47.103.194.209:27017/?authMechanism=DEFAULT&authSource=centerController')  # 默认连接到本地主机的27017端口
    if client is None:
        print("连接失败")
        return None
    else:
        print("连接成功")
        db = client['centerController']
        # 获取数据库实例
        return db

