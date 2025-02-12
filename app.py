from flask import Flask, abort

app = Flask(__name__)

@app.route('/<uname>')
def index(uname):
    if uname[0].isdigit():
        abort(400)
    return '<h1>good username</h1>'

@app.route('/main/<uname>')
def main(uname):
    if uname[0].isdigit():
        abort(403)
    return '<h1>cool username</h1>'


if __name__ == '__main__':
    app.run()