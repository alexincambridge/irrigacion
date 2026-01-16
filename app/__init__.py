from flask import Flask
from flask_login import LoginManager
from app.models import init_db
from app.auth import auth, get_user_by_id
from app.routes import routes
from app.config import SECRET_KEY

def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    init_db()

    login = LoginManager(app)
    login.login_view = "auth.login"

    @login.user_loader
    def load_user(user_id) :
        return get_user_by_id(user_id)

    app.register_blueprint(auth)
    app.register_blueprint(routes)

    return app
