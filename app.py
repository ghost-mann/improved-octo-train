from flask import Flask, render_template, url_for
from flask_login import current_user
from dataclasses import dataclass
from typing import List
app = Flask(__name__)

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

@app.context_processor # can inject variables in every route
def inject_dict_for_all_templates():
    # navbar
    nav = [
        {"text":"Home", "url": url_for('index')},
        {"text":"About", "url": url_for('about')},
        {"text": "Shop", "url": url_for('shop')},
        {"text": "Login/Sign Up",
         "sublinks" : [
             {"text": "Login", "url": "https://stackoverflow.com"},
             {"text": "Account Settings", "url": "https://google.com"},
             {"text": "My Orders", "url": "https://google.com"},
             {"text": "Sign Out", "url": "https://google.com"},
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

# login placeholder
@app.route('/login')
def login():
    return 'login page placeholder'

if __name__ == '__main__':
    app.run(debug=True)
