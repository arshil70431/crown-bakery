from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from models import db, User, Product, Order, OrderItem
from config import Config
import razorpay
import json
import hashlib
import hmac

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Initialize Razorpay client
client = razorpay.Client(auth=(app.config['RAZORPAY_KEY_ID'], app.config['RAZORPAY_KEY_SECRET']))

# ------------------ Helper Functions ------------------
def get_cart():
    """Retrieve cart from session (list of dicts {product_id, quantity})"""
    return session.get('cart', [])

def save_cart(cart):
    session['cart'] = cart
    session.modified = True

def get_product_by_id(product_id):
    return Product.query.get(product_id)

def get_cart_items_with_details():
    cart = get_cart()
    items = []
    total = 0
    for item in cart:
        product = get_product_by_id(item['product_id'])
        if product:
            subtotal = product.price * item['quantity']
            total += subtotal
            items.append({
                'product': product,
                'quantity': item['quantity'],
                'subtotal': subtotal
            })
    return items, total

# ------------------ Seed Products (run once) ------------------
def seed_products():
    if Product.query.count() == 0:
        products_data = [
            # Western
            {'name': 'Artisan Bread', 'description': 'Our signature sourdough bread, made with a 100-year-old starter.', 'price': 350, 'image_url': 'https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=600&q=80', 'category': 'western'},
            {'name': 'Chocolate Cake', 'description': 'Three layers of moist chocolate cake with rich ganache.', 'price': 999, 'image_url': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600&q=80', 'category': 'western'},
            {'name': 'Chocolate Croissants', 'description': 'Buttery, flaky croissants filled with Belgian chocolate.', 'price': 180, 'image_url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTe1G2KS3I1lqgLWvxawWqvLYBy8NDOadWWJQ&s', 'category': 'western'},
            {'name': 'Caramel Macarons', 'description': 'Delicate almond meringue with rich caramel filling.', 'price': 140, 'image_url': 'https://annabanana.co/wp-content/uploads/2022/11/Salted-Caramel-Macarons-Feat-17.jpg', 'category': 'western'},
            {'name': 'Gourmet Cookies', 'description': 'Butter pecan, chocolate chunk, double chocolate, and more.', 'price': 60, 'image_url': 'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=600&q=80', 'category': 'western'},
            {'name': 'Cinnamon Rolls', 'description': 'Soft, fluffy rolls with cinnamon sugar and cream cheese frosting.', 'price': 210, 'image_url': 'https://images.unsplash.com/photo-1534620808146-d33bb39128b2?w=600&q=80', 'category': 'western'},
            # Indian
            {'name': 'Samosa Puffs', 'description': 'Flaky pastry filled with spiced potatoes and peas.', 'price': 45, 'image_url': 'https://www.thespruceeats.com/thmb/U672mnDBTpBWPTI7DJun6OL3tHs=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/easy-vegetable-samosas-recipe-2098695-hero-01-fa7ef71f7c604698825081a01720ee2a.jpg', 'category': 'indian'},
            {'name': 'Paneer Puff', 'description': 'Flaky pastry filled with spiced paneer and vegetables.', 'price': 120, 'image_url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRoUc_VHYbBQTHPOf1LXGb23gJYCOL4CsLzbQ&s', 'category': 'indian'},
            {'name': 'Masala Khari', 'description': 'Flaky, savory biscuits seasoned with Indian spices.', 'price': 85, 'image_url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTGIABIKumVcuHvZjAiu8VKMLsRWVrf5IODKw&s', 'category': 'indian'},
            {'name': 'Laadi Pav', 'description': 'Soft, fluffy Mumbai-style bread rolls.', 'price': 40, 'image_url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSRsQY70BpQuHIiBFv2Kodi6_3WuxzdujVkhA&s', 'category': 'indian'},
            {'name': 'Fresh Bread', 'description': 'Freshly baked daily bread, perfect for sandwiches or toast.', 'price': 75, 'image_url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSf-LyQBJhbPExm-8GhKeDsB-4bH367Sgapqw&s', 'category': 'indian'},
            {'name': 'Butter Toast', 'description': 'Crispy, golden brown toast with a generous layer of butter.', 'price': 35, 'image_url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS7_qf08W_PQYYoWY6oi07FIgxhk6yvxSQiNg&s', 'category': 'indian'},
        ]
        for p in products_data:
            product = Product(**p)
            db.session.add(product)
        db.session.commit()
        print("✅ Products seeded successfully")

# ------------------ Routes ------------------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/products')
def products():
    # Get all products for display
    all_products = Product.query.all()
    return render_template('products.html', products=all_products)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/checkout')
def checkout():
    cart_items, total = get_cart_items_with_details()
    return render_template('checkout.html', cart_items=cart_items, total=total)

# ------------------ Cart API (session based) ------------------
@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    if not product_id:
        return jsonify({'error': 'Product ID required'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    cart = get_cart()
    # Check if product already in cart
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            save_cart(cart)
            return jsonify({'message': 'Cart updated', 'cart': cart})

    cart.append({'product_id': product_id, 'quantity': quantity})
    save_cart(cart)
    return jsonify({'message': 'Item added to cart', 'cart': cart})

@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    if not product_id:
        return jsonify({'error': 'Product ID required'}), 400

    cart = get_cart()
    cart = [item for item in cart if item['product_id'] != product_id]
    save_cart(cart)
    return jsonify({'message': 'Item removed', 'cart': cart})

@app.route('/api/cart/update', methods=['POST'])
def update_cart_quantity():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    if not product_id or quantity is None:
        return jsonify({'error': 'Product ID and quantity required'}), 400

    cart = get_cart()
    for item in cart:
        if item['product_id'] == product_id:
            if quantity <= 0:
                cart.remove(item)
            else:
                item['quantity'] = quantity
            save_cart(cart)
            return jsonify({'message': 'Cart updated', 'cart': cart})
    return jsonify({'error': 'Item not in cart'}), 404

@app.route('/api/cart', methods=['GET'])
def get_cart_api():
    items, total = get_cart_items_with_details()
    return jsonify({
        'items': [{
            'product_id': item['product'].id,
            'name': item['product'].name,
            'price': item['product'].price,
            'quantity': item['quantity'],
            'subtotal': item['subtotal']
        } for item in items],
        'total': total
    })

# ------------------ Razorpay Payment Routes ------------------
@app.route('/create-order', methods=['POST'])
def create_order():
    data = request.get_json()
    amount = data.get('amount')  # in paise (INR)
    if not amount:
        return jsonify({'error': 'Amount required'}), 400

    # Create Razorpay Order
    order_data = {
        'amount': int(amount * 100),  # convert to paise
        'currency': 'INR',
        'payment_capture': '1'  # auto capture
    }
    try:
        order = client.order.create(data=order_data)
        return jsonify({
            'order_id': order['id'],
            'razorpay_key': app.config['RAZORPAY_KEY_ID'],
            'amount': order['amount']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/payment-callback', methods=['POST'])
def payment_callback():
    # Verify Razorpay signature
    razorpay_payment_id = request.form.get('razorpay_payment_id')
    razorpay_order_id = request.form.get('razorpay_order_id')
    razorpay_signature = request.form.get('razorpay_signature')

    # Prepare the signature verification
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': razorpay_signature
    }

    # Verify signature
    try:
        client.utility.verify_payment_signature(params_dict)
        # Payment successful – now create order in our database
        # Get cart items
        cart_items, total = get_cart_items_with_details()
        if not cart_items:
            return jsonify({'error': 'Cart is empty'}), 400

        # Create order record
        order = Order(
            total_amount=total,
            payment_id=razorpay_payment_id,
            order_id=razorpay_order_id,
            payment_status='Paid',
            # billing details from the form can be added if sent
        )
        db.session.add(order)
        db.session.flush()  # get order.id

        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product'].id,
                quantity=item['quantity'],
                price=item['product'].price
            )
            db.session.add(order_item)

        # Clear cart
        session['cart'] = []
        session.modified = True

        db.session.commit()
        return jsonify({'status': 'success', 'order_id': order.id})

    except Exception as e:
        # Signature verification failed or other error
        return jsonify({'error': str(e)}), 400

# ------------------ Place Order (final step) ------------------
@app.route('/place-order', methods=['POST'])
def place_order():
    # This route is called after successful payment (or for Cash on Delivery)
    data = request.get_json()
    payment_method = data.get('payment_method')
    if payment_method == 'cod':
        # For COD, we directly create order without Razorpay
        cart_items, total = get_cart_items_with_details()
        if not cart_items:
            return jsonify({'error': 'Cart is empty'}), 400

        order = Order(
            total_amount=total,
            payment_status='Pending (COD)',
            billing_name=data.get('billing_name'),
            billing_email=data.get('billing_email'),
            billing_phone=data.get('billing_phone'),
            billing_address=data.get('billing_address'),
            billing_city=data.get('billing_city'),
            billing_state=data.get('billing_state'),
            billing_zip=data.get('billing_zip')
        )
        db.session.add(order)
        db.session.flush()
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product'].id,
                quantity=item['quantity'],
                price=item['product'].price
            )
            db.session.add(order_item)
        session['cart'] = []
        session.modified = True
        db.session.commit()
        return jsonify({'status': 'success', 'order_id': order.id})
    else:
        # For online payment, we already handled in payment-callback
        return jsonify({'error': 'Invalid payment method'}), 400

# ------------------ Run the app ------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_products()
    app.run(debug=True)