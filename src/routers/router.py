from src.routers.user.user_router import user_bp
from src.routers.auth.auth_router import auth_bp
from src.routers.project.project_router import project_bp
def register_blueprints(app):
    # 注册用户路由蓝图
    app.register_blueprint(user_bp)
    # 注册认证路由蓝图
    app.register_blueprint(auth_bp)
    # 注册项目路由蓝图
    app.register_blueprint(project_bp)

    return app
