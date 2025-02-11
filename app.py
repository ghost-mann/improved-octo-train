from flask import Flask
app = Flask(__name__)

@app.route('/')
def msg():
    return 'hello'
app.run(debug=True)