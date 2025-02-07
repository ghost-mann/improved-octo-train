from flask import Flask,render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        if (request.args.get('num') == None):
            return render_template('index.html')

        elif(request.args.get('num') == None):
            return "<html><body><h1>Invalid Request</h1></body></html>"
        else:
            number = request.args.get('num')
            sq = int(number) * int(number)
            return render_template('answer.html', squareofnum=sq, num=number)

if(__name__ == '__main__'):
    app.run(debug=True)