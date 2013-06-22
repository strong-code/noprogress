from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

import venusian

import noprogress

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("noprogress.default_settings")
app.config.from_envvar("NOPROGRESS_SETTINGS")
db = SQLAlchemy(app)

if app.debug:
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)

scanner = venusian.Scanner()
scanner.scan(noprogress)

def main():
    app.run()
