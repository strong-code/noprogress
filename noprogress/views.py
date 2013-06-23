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


@app.route("/api/workouts")
def api_workouts():
    user = g.identity

    offset = int(flask.request.args.get("offset", 0))
    limit = int(flask.request.args.get("limit", -1))

    q = user.workouts.offset(offset)
    if limit > -1:
        q = q.limit(limit)

    return flask.jsonify({
        "total": user.workouts.count(),
        "workouts": [x.to_api() for x in q]
    })


@app.route("/api/last")
def api_last():
    user = g.identity

    return flask.jsonify({l.name: l.to_api()["sets"] for l in user.find_last()})


@app.route("/api/log", methods=["POST"])
def log():
    log = flask.request.json.get("log", None)

    try:
        workout = slf.parse_workout(log)
    except Exception:
        flask.abort(400)

    session = db.session()
    w = Workout(user=g.identity,
                date=datetime.datetime.strptime(workout["date"], "%Y-%m-%d").date(),
                comment=workout["comment"])

    for i, lift in enumerate(workout["lifts"]):
        l = Lift(workout=w, name=lift["name"].lower().replace(" ", "_"), order=i)
        session.add(l)

        for j, set in enumerate(lift["sets"]):
            s = Set(lift=l, weight=set["weight"], reps=set["reps"], order=j)
            session.add(s)

    session.commit()

    return flask.jsonify({
        "status": "ok"
    })


@app.route("/dashboard")
def dashboard():
    if g.identity is None:
        return flask.redirect(flask.url_for(".home"))

    return flask.render_template("dashboard.html")


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
