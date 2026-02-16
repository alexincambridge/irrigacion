from flask import Flask
from flask_login import LoginManager

from app.auth import auth, init_login_manager
from app.routes import routes
from app.irrigation import irrigation
from app.db import close_db
from app.hardware import all_off


def create_app():
    app = Flask(__name__)

    # 🔒 Seguridad: apagar todas las zonas al arrancar
    all_off()

    app.secret_key = "dev-secret"

    app.register_blueprint(auth)
    app.register_blueprint(routes)
    app.register_blueprint(irrigation)

    app.teardown_appcontext(close_db)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    init_login_manager(login_manager)

    return app
