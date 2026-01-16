from flask import Flask
from flask_login import LoginManager
from app.models import init_db
from app.auth import auth, get_user_by_id
from app.routes import routes
from app.config import SECRET_KEY
import os

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))

    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static")
    )

    app.secret_key = SECRET_KEY
    init_db()

    login = LoginManager()
    login.init_app(app)
    login.login_view = "auth.login"

    @login.user_loader
    def load_user(user_id):
        return get_user_by_id(user_id)

    app.register_blueprint(auth)
    app.register_blueprint(routes)

    return app
