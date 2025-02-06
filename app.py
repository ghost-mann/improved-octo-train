import click
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import errno
import os
from sqlalchemy.orm import DeclarativeBase, mapped_column

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
# configure sqlite db
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"

db = SQLAlchemy(model_class=Base) # instance of sqlalchemy


# defining models
class Event(db.Model):
    date = mapped_column(db.String, primary_key=True)
    event = mapped_column(db.String)

db.init_app(app) # linking sqlalchemy instance to flask app

@app.cli.command('initdb')
def initdb():
    # create the db
    with app.app_context():
        db.create_all()
        click.echo('Initialized the database.')

@app.route('/')
def index(): # view functions
    return '<h1>hello world </h1>'

@app.route('/user/<name>')
def user(name):
    return '<h1>Hello %s</h1>' % name

if __name__ == '__main__' :
    app.run(debug=True)