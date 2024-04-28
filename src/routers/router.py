from src.routers.user.user_router import user_bp


def register_blueprints(app):
    app.register_blueprint(user_bp)

    return app
