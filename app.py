from flask import Flask
app = Flask(__name__)

@app.route('/')
def msg():
    return 'hello'

@app.route('/vstring/<name>')
def string(name):
    return "my name is %s" % name

app.run(debug=True)