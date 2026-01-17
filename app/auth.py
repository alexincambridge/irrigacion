from flask import Blueprint, render_template, request, redirect
from flask_login import login_user, logout_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import get_db

auth = Blueprint("auth", __name__)

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

def get_user_by_id(user_id):
    db = get_db()
    row = db.execute(
        "SELECT id, username FROM users WHERE id=?",
        (user_id,)
    ).fetchone()
    return User(row[0], row[1]) if row else None

@auth.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        row = db.execute(
            "SELECT id, username, password FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if row and check_password_hash(row[2], password):
            login_user(User(row[0], row[1]))
            return redirect("/")
        else:
            error = "Usuario o contraseña incorrectos"

    return render_template("login.html", error=error)

@auth.route("/logout")
def logout():
    logout_user()
    return redirect("/login")
