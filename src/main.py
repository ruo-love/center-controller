from flask import Flask
from src.db.connect import connect
from src.routers.router import register_blueprints


# 创建 Flask 应用
def create_app():
    app = Flask(__name__)

    # 注册路由蓝图
    register_blueprints(app)

    # 初始化数据库连接和调度器
    with app.app_context():
        app.db = connect()  # 连接数据库

    return app


if __name__ == '__main__':
    # 创建 Flask 应用实例
    app = create_app()
    # 启动 Flask 应用
    app.run(debug=True)

