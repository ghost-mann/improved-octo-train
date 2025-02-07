import datetime
import click
from flask import Flask,redirect,render_template,request,url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column

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

@app.route('/', methods=['GET', 'POST'])
def index():
        if(request.method == 'POST'):
            db.session.add(Event(date=datetime.datetime.now().__str__(), event=request.form['eventBox']))
            db.session.commit()
            return redirect(url_for('index'))
        return render_template('index.html', eventsList=db.session.execute(db.select(Event).order_by(Event.date)).scalars()) # GET


# starts development server
if __name__ == '__main__' :
    app.run(debug=True)