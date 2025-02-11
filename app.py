from flask import Flask
app = Flask(__name__)

@app.route('/')
def msg():
    return 'hello'

@app.route('/vint/<int:age>')
def vint(age):
    return "my age is %d" % age

app.run(debug=True)