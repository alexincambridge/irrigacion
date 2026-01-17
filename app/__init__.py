from flask import Flask
from flask_login import LoginManager
from app.models import close_db
from app.routes import routes
from app.auth import auth, get_user_by_id

def create_app():
    app = Flask(__name__)
    app.secret_key = "change-this"

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(user_id)

    app.register_blueprint(auth)
    app.register_blueprint(routes)

    app.teardown_appcontext(close_db)

    return app
