from flask import Flask, render_template, url_for, request, redirect, session
from flask_login import current_user
from dataclasses import dataclass
from typing import List
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"

@dataclass
class User:
    id: int
    username: str
    password: str
    email: str

# Simple in-memory user storage
users = []

@dataclass
class Product:
    id: int
    name: str
    description: str
    price: float
    image_url: str
    category: str

products = [
    Product(1, "Beaded Necklace", "Hand-crafted Maasai beaded necklace", 29.99, "/static/images/necklace.jpg", "Jewelry"),
    Product(2, "Woven Basket", "Traditional African woven basket", 49.99, "/static/images/basket.jpg", "Home Decor"),
    Product(3, "Carved Statue", "Wooden hand-carved statue", 79.99, "/static/images/statue.jpg", "Art"),
    Product(4, "Leather Bag", "Handmade leather tote bag", 89.99, "/static/images/bag.jpg", "Accessories"),
    Product(5, "Fabric Wall Art", "Traditional African fabric wall hanging", 59.99, "/static/images/wall-art.jpg", "Home Decor"),
    Product(6, "Beaded Bracelet", "Colorful beaded bracelet set", 19.99, "/static/images/bracelet.jpg", "Jewelry"),
]

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
    categories = list(set(product.category for product in products))
    return render_template('shop.html', products=products, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        user = next((user for user in users if user.username == username), None)

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

        if any(user.username == username for user in users):
            return render_template("register.html", message="Username already exists")

        # Create new user
        user_id = len(users) + 1
        hashed_password = generate_password_hash(password)
        new_user = User(id=user_id, username=username, password=hashed_password, email=email)
        users.append(new_user)

        return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
