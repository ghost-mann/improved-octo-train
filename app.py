from flask import Flask
app = Flask(__name__)

@app.route('/')
def msg():
    return 'hello'

@app.route('/vfloat/<float:weight>')
def vfloat(weight):
    return "my weight is %f" % weight

app.run(debug=True)