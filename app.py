from crypt import methods

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
                {"text": "My Basket", "url": url_for('cart')},
                {"text": "My Orders", "url": url_for('user_orders')},
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

@app.route('/shop', methods=['GET', 'POST'])
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

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/cart/remove/<int:cart_item_id>')
@login_required
def remove_from_cart(cart_item_id):
    cart_item = CartItem.query.filter_by(
        id=cart_item_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart!', 'info')
    return redirect(url_for('view_cart'))

@app.route('/cart/update/<int:cart_item_id>', methods=['POST'])
@login_required
def update_cart_item(cart_item_id):
    quantity = request.form.get('quantity', type=int)

    cart_item = CartItem.query.get_or_404(cart_item_id)

    if quantity is not None and quantity > 0:
        cart_item.quantity = quantity
        db.session.commit()
        flash('Cart item updated successfully!', 'success')
    else:
        flash('Invalid quantity!', 'danger')

    return redirect(url_for('cart'))
@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('cart'))

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    order = Order(
        user_id=current_user.id,
        total_price=total_price,
        status='Pending'
    )
    db.session.add(order)
    db.session.commit()

    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product.id,
            quantity=cart_item.quantity,
            price=cart_item.product.price,
        )
        db.session.add(order_item)

    for cart_item in cart_items:
        db.session.delete(cart_item)

    db.session.commit()
    flash('Order placed successfully!', 'success')
    return redirect(url_for('order_confirmation', order_id=order.id))


@app.route('/orders')
@login_required
def user_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('user_orders.html', orders=orders)


@app.route('/order/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template('order_confirmation.html', order=order)


# Admin Order Management
@app.route('/admin/orders')
@login_required
def admin_orders():
    if not current_user.admin:
        abort(403)
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)


@app.route('/admin/orders/<int:order_id>/update_status', methods=['POST'])
@login_required
def update_order_status(order_id):
    if not current_user.admin:
        abort(403)

    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')

    order.status = new_status
    db.session.commit()

    flash(f'Order status updated to {new_status}', 'success')
    return redirect(url_for('admin_orders'))

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

@app.route('/admin/orders/<int:order_id>')
@login_required

def admin_order_detail(order_id):
    # Get specific order
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)

@app.route('/admin/orders/<int:order_id>/update', methods=['POST'])
@login_required

def admin_update_order(order_id):
    order = Order.query.get_or_404(order_id)
    status = request.form.get('status')

    if status:
        order.status = status
        db.session.commit()
        flash('Order status updated successfully')

    return redirect(url_for('admin_order_detail', order_id=order_id))
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
