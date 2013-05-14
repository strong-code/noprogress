#all our imports
import sqlite3
from flask import Flask, render_template

#config file location
APP_CONFIG = '/config.ini'

app = Flask(__name__)
app.config.from_envvar=('APP_CONFIG', silent = FALSE)

def db_connect:
	return sqlite3.connect(app.config['DATABASE'])

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()