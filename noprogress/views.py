import flask
import requests
import json
import datetime
import math

from flask import g

from . import app, db
from . import slf
from models import User, Workout, Set, Lift


@app.route("/")
def home():
    if g.identity is None:
        return flask.render_template("landing.html")

    return flask.redirect(flask.url_for(".dashboard"))


@app.route("/dashboard")
def dashboard():
    user = g.identity

    total_count = user.workouts.count()
    limit = 5
    page = int(flask.request.args.get("page", 1))

    return flask.render_template("dashboard.html", total_count=total_count, user=user, limit=limit,
                                 page=page, total_pages=int(math.ceil(total_count / float(limit))))


@app.route("/auth/login", methods=["POST"])
def login():
    if "assertion" not in flask.request.form:
        flask.abort(400)

    data = {
        "assertion": flask.request.form["assertion"],
        "audience": app.config["PERSONA_AUDIENCE"]
    }
    resp = requests.post("https://verifier.login.persona.org/verify",
                         data=data,
                         verify=True)

    if resp.ok:
        verification_data = json.loads(resp.content)

        if verification_data["status"] == "okay":
            email = flask.session["identity_email"] = verification_data["email"]

            # Check if the user exists -- if not, create him.
            u = User.by_email(email)
            if u is None:
                u = User(email=email)
                s = db.session()
                s.add(u)
                s.commit()

            return "okay"

    flask.abort(500)


@app.route("/auth/logout", methods=["POST"])
def logout():
    try:
        del flask.session["identity_email"]
    except KeyError:
        pass

    return "okay"


@app.route("/log", methods=["POST"])
def log():
    try:
        workout = slf.parse_workout(flask.request.form["log"])
    except:
        return "error"

    # FUCK TRANSACTIONS 2013
    session = db.session()
    w = Workout(user_id=g.identity.id,
                date=datetime.datetime.strptime(workout["date"], "%Y-%m-%d").date(),
                comment=workout["comment"])
    session.add(w)
    session.commit()

    for i, lift in enumerate(workout["lifts"]):
        l = Lift(workout_id=w.id, name=lift["name"].lower().replace(" ", "_"), order=i)
        session.add(l)
        session.commit()

        for j, set in enumerate(lift["sets"]):
            s = Set(lift_id=l.id, weight=set["weight"], reps=set["reps"], order=j)
            session.add(s)

        session.commit()

    return "ok"
