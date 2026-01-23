from flask import Flask
from flask_login import LoginManager
from app.auth import auth, init_login_manager
from app.routes import routes

def create_app():
    app = Flask(__name__)
    app.secret_key = "dev-secret"

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    init_login_manager(login_manager)

    app.register_blueprint(auth)
    app.register_blueprint(routes)

    return app
