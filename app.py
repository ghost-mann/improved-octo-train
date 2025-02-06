from flask import Flask
import errno
import os
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
@app.route('/')
def index(): # view functions
    return '<h1>hello world </h1>'

@app.route('/user/<name>')
def user(name):
    return '<h1>Hello %s</h1>' % name

if __name__ == '__main__' :
    app.run(debug=True)