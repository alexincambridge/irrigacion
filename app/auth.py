from flask import Blueprint, render_template, request, redirect
from flask_login import login_user, logout_user, UserMixin
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


@auth.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        db = get_db()
        u = db.execute(
            "SELECT id,username FROM users WHERE username=? AND password=?",
            (request.form["username"], request.form["password"])
        ).fetchone()
        if u:
            login_user(User(u[0], u[1]))
            return redirect("/")

    return render_template("login.html")

@auth.route("/logout")
def logout():
    logout_user()
    return redirect("/login")
