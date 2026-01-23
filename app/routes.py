from flask import Blueprint, render_template
from flask_login import login_required

routes = Blueprint("routes", __name__)

@routes.route("/")
@login_required
def dashboard():
    return "<h1>DASHBOARD OK</h1>"
