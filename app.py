from flask import Flask, render_template, url_for, request, redirect, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from models import User, Products, db
from datetime import datetime
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.context_processor
def inject_dict_for_all_templates():
    nav = [
        {"text": "Home", "url": url_for('index')},
        {"text": "About", "url": url_for('about')},
        {"text": "Shop", "url": url_for('shop')},
        {"text": "Login/Sign Up",
         "sublinks": [
             {"text": "Login", "url": url_for('login')},
             {"text": "Register", "url": url_for('register')},
             {"text": "Account Settings", "url": url_for('login')},
             {"text": "My Orders", "url": url_for('login')},
             {"text": "Sign Out", "url": url_for('logout')},
         ],
         },
    ]
    return dict(navbar=nav)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/shop')
def shop():
    products = Products.query.all()
    categories = db.session.query(Products.category).distinct()
    return render_template('shop.html', products=products, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            return render_template("login.html", message="Wrong username or password")
    return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        if not (username and password and email):
            return render_template("register.html", message="Please fill out all required fields")

        if User.query.filter_by(username=username).first():
            return render_template("register.html", message="Username already exists")

        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            password=hashed_password,
            email=email,
            created_at=datetime.utcnow(),
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
