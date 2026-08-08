from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(200), nullable=False)  # store hashed in production
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(300))
    category = db.Column(db.String(50))  # 'western' or 'indian'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    payment_id = db.Column(db.String(100))          # Razorpay payment ID
    order_id = db.Column(db.String(100))            # Razorpay order ID
    payment_status = db.Column(db.String(20), default='Pending')
    billing_name = db.Column(db.String(100))
    billing_email = db.Column(db.String(100))
    billing_phone = db.Column(db.String(20))
    billing_address = db.Column(db.Text)
    billing_city = db.Column(db.String(50))
    billing_state = db.Column(db.String(50))
    billing_zip = db.Column(db.String(20))

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)   # price at time of order