from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, LoginManager
from app.models import User

auth = Blueprint("auth", __name__)

USERS = {
    "admin": {"id": 1, "password": "admin"}
}

def init_login_manager(login_manager):

    @login_manager.user_loader
    def load_user(user_id):
        if user_id == "1":
            return User(1, "admin")
        return None


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if u in USERS and USERS[u]["password"] == p:
            user = User(USERS[u]["id"], u)
            login_user(user)
            return redirect(url_for("routes.dashboard"))

    return render_template("login.html")


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
