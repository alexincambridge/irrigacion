from flask import Flask
from app.models import close_db
from app.routes import routes
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    app.secret_key = "dev-secret"

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    app.register_blueprint(routes)

    app.teardown_appcontext(close_db)

    return app
