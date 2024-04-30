from flask import Flask
from src.db.connect import connect
from src.routers.router import register_blueprints


# 创建 Flask  应用
def create_app():
    app = Flask(__name__)
    register_blueprints(app)
    # 将数据库连接存储在应用上下文中

    with app.app_context():
        app.db = connect()
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
