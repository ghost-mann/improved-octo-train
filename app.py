from flask import Flask, render_template, url_for
from flask_login import current_user
app = Flask(__name__)
@app.context_processor # can inject variables in every route
def inject_dict_for_all_templates():
    # navbar
    nav = [
        {"text":"Home", "url": url_for('index')},
        {"text":"About", "url": url_for('about')},
        {
            "text":"More",
            "sublinks" : [
                {"text": "Stack Overflow","url":"https://stackoverflow.com"},
                {"text": "Google", "url":"https://google.com"},
            ],
        },
        {"text": "Login", "url": url_for('login')}
    ]
    return dict(navbar=nav)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# login placeholder
@app.route('/login')
def login():
    return 'login page placeholder'

if __name__ == '__main__':
    app.run(debug=True)
