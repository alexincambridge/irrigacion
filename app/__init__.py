from flask import Flask
from flask_login import LoginManager
from app.auth import auth, init_login_manager
from app.hardware import irrigation_off
from app.routes import routes
from app.gpio import relay_off
from app.models import get_db


def create_app() :
    app = Flask(__name__)
    irrigation_off()
    app.secret_key = "dev-secret"

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    init_login_manager(login_manager)

    app.register_blueprint(auth)
    app.register_blueprint(routes)

    return app


def ensure_all_off() :
    db = get_db()
    zones = db.execute("SELECT gpio_pin FROM irrigation_zones").fetchall()
    for z in zones :
        relay_off(z["gpio_pin"])
