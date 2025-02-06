from flask import Flask
from sqlalchemy import SQLAlchemy
import errno
import os
from sqlalchemy.orm import DeclarativeBase

# instance folder path
instance = os.path.join(os.path.dirname(__file__), 'instance')

# instance directory
try:
    os.mkdir(instance)
except OSError as exc:
    if exc.errno != errno.EEXIST:
        raise
    pass
app = Flask(__name__)


class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base) # instance of sqlalchemy
db.init_app(app) # linking sqlalchemy instance to flask app

# configure sqlite db
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)

@app.route('/')
def index(): # view functions
    return '<h1>hello world </h1>'

@app.route('/user/<name>')
def user(name):
    return '<h1>Hello %s</h1>' % name

if __name__ == '__main__' :
    app.run(debug=True)