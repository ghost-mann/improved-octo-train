from flask import Flask, render_template, url_for, request, redirect, session, abort, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from models import User, Products, db, Order, CartItem, OrderItem
from datetime import datetime
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.context_processor
def inject_dict_for_all_templates():
    from flask_login import current_user
    nav = [
        {"text": "Home", "url": url_for('index')},
        {"text": "About", "url": url_for('about')},
        {"text": "Shop", "url": url_for('shop')},
    ]

    if current_user.is_authenticated:
        account_dropdown = {
            "text": current_user.username,
            "sublinks": [
                {"text": "Account Settings", "url": url_for('account_settings')},
                {"text": "My Orders", "url": '#'},
                {"text": "Sign Out", "url": url_for('logout')},
            ]
        }
        if current_user.admin:
            account_dropdown["sublinks"].insert(0,
                                                {"text": "Admin Panel", "url": url_for('admin_dashboard')})
        nav.append(account_dropdown)
    else:
        nav.append({
            "text": "Login/Sign Up",
            "sublinks": [
                {"text": "Login", "url": url_for('login')},
                {"text": "Register", "url": url_for('register')},
            ]
        })

    return dict(navbar=nav)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/shop')
def shop():
    # products = Products.query.all()
    category = request.args.get('category')
    categories = db.session.query(Products.category).distinct()
    if category:
        products = Products.query.filter_by(category=category).all()
    else:
        products = Products.query.all()
    return render_template('shop.html', products=products, categories=categories)

@app.route('/cart/add', methods=['POST'])
@login_required
def cart_add():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))

    product = Products.query.get_or_404(product_id)

    existing_cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=product_id,
    ).first()

    if existing_cart_item:
        existing_cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity,
        )
        db.session.add(cart_item)
    db.session.commit()
    flash('Product added to cart successfully!', 'success')
    return redirect(url_for('shop'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.admin:
                return redirect(url_for('admin_dashboard'))
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

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.admin:
        abort(403)
    return render_template('admin/dashboard.html')

@app.route('/admin/products')
@login_required
def admin_products():
    if not current_user.admin:
        abort(403)
    products = Products.query.join(User, Products.user_id == User.id, isouter=True).all()
    return render_template('admin/products.html', products=products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.admin:
        abort(403)

    # category list
    categories = ['Clothing', 'Artefacts', 'Shoe wear', 'Jewellery']
    if request.method == 'POST':
        new_product = Products(
            name=request.form['name'],
            description=request.form['description'],
            price=float(request.form['price']),
            category =request.form['category'],
            image_url=request.form['image_url'],
            quantity=0,
            created_at=datetime.utcnow(),
            user_id=current_user.id
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('admin_products'))
    return render_template('admin/add_product.html', categories=categories)

@app.route('/admin/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    if not current_user.admin:
        abort(403)
    categories = ['Clothing', 'Artefacts', 'Shoe wear', 'Jewellery']
    product = Products.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        product.category = request.form['category']
        product.image_url = request.form['image_url']
        db.session.commit()
        return redirect(url_for('admin_products'))
    return render_template('admin/edit_product.html', product=product, categories=categories)

@app.route('/admin/products/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    if not current_user.admin:
        abort(403)
    product = Products.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin_products'))

# User Management
@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.admin:
        abort(403)
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/toggle_admin/<int:id>', methods=['POST'])
@login_required
def toggle_admin(id):
    if not current_user.admin:
        abort(403)
    user = User.query.get_or_404(id)
    user.admin = not user.admin
    db.session.commit()
    return redirect(url_for('admin_users'))

@app.route('/admin/users/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if not current_user.admin:
        abort(403)
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin_users'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account_settings():
    if request.method == 'POST':
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        new_email = request.form.get("email")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        phone = request.form.get("phone")
        address = request.form.get("address")

        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.phone = phone
        current_user.address = address

        if current_password and not check_password_hash(current_user.password, current_password):
            return render_template('account.html', message="Wrong password", message_category="error")

        if new_email and new_email != current_user.email:
            if User.query.filter_by(email=new_email).first():
                return render_template('account.html', message="Email already exists", message_category="error")
            current_user.password = generate_password_hash(new_password)

        db.session.commit()
        return render_template('account.html', message="Account settings updated", message_category="success")

    return render_template('account.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
