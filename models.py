from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    admin = db.Column(db.Boolean, default=False)
    is_seller = db.Column(db.Boolean, default=False)  # New field to identify sellers
    artist_bio = db.Column(db.Text)  # Artist description/bio
    artist_website = db.Column(db.String(200))  # Artist's website/portfolio


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)


class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # foreign key to artist/seller
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # access user info
    user = db.relationship('User', backref=db.backref('products', lazy='dynamic'))
    # access category info
    category_rel = db.relationship('Category', backref='products')
    # Product status (active, inactive, etc.)
    status = db.Column(db.String(20), default='active')


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    # accessing user and product info
    user = db.relationship('User', backref='cart_items')
    product = db.relationship('Products', backref='cart_items')
    added_at = db.Column(db.DateTime, default=datetime.utcnow)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    shipping_address = db.Column(db.String(200))
    tracking_number = db.Column(db.String(100))
    # accessing user and ordered items
    user = db.relationship('User', backref='orders')
    order_items = db.relationship('OrderItem', backref='order', lazy='dynamic')


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Track the seller directly
    product = db.relationship('Products', backref='order_items')
    seller = db.relationship('User', foreign_keys=[seller_id])


# For artist-specific metrics and payouts
class SellerTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_item_id = db.Column(db.Integer, db.ForeignKey('order_item.id'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')  # Pending, Paid, Failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    seller = db.relationship('User', backref='transactions')
    order_item = db.relationship('OrderItem', backref='transactions')
    description = db.Column(db.String(200))