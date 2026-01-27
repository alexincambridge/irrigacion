from flask import render_template


@routes.route("/sensors")
@login_required
def dashboard():
    return render_template("sensors.html")
