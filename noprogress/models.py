import flask
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from . import app, db


class IdMixin(object):
    """
    A mixin for entities that want a primary key.
    """
    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def by_id(cls, id):
        """
        Retrieve an entity by its primary key.
        """
        try:
            return db.session.query(cls).filter(cls.id == id).one()
        except (NoResultFound, MultipleResultsFound):
            return None


class User(db.Model, IdMixin):
    __tablename__ = "users"

    email = db.Column(db.String, unique=True, nullable=False)

    @classmethod
    def by_email(cls, email):
        """
        Retrieve a user by his email.
        """
        try:
            return db.session.query(cls).filter(cls.email == email).one()
        except (NoResultFound, MultipleResultsFound):
            return None

    @classmethod
    def current_identity(cls):
        email = flask.session.get("identity_email")
        if email is None:
            return None
        return cls.by_email(email)


@app.context_processor
def inject_identity():
    identity = User.current_identity()
    return {
        "identity": identity,
        "identity_email": identity.email if identity is not None \
                                         else None
    }


class Workout(db.Model, IdMixin):
    __tablename__ = "workouts"

    date = db.Column(db.Date, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("User", backref=db.backref("workouts",
                                                      cascade="all, delete, delete-orphan"))


class Lift(db.Model, IdMixin):
    __tablename__ = "lifts"

    name = db.Column(db.String, nullable=False)
    order = db.Column(db.Integer, nullable=False)

    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"), nullable=False)

    workout = db.relationship("Workout", backref=db.backref("lifts",
                                                            cascade="all, delete, delete-orphan"))


class Set(db.Model, IdMixin):
    __tablename__ = "sets"

    weight = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    order = db.Column(db.Integer, nullable=False)

    lift_id = db.Column(db.Integer, db.ForeignKey("lifts.id"), nullable=False)

    lift = db.relationship("Lift", backref=db.backref("sets",
                                                      cascade="all, delete, delete-orphan"))