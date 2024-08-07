from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests
from google_auth_oauthlib.flow import Flow
from functools import wraps
from flask import Flask, request, render_template, send_file
import pandas as pd
import jsonify 
from math import ceil
from bson import ObjectId
from datetime import datetime


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# MongoDB setup
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['ecommerce_db']

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Google OAuth setup
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

flow = Flow.from_client_secrets_file(
    'client_secrets.json',
    scopes=['openid', 'email', 'profile'],
    redirect_uri='http://localhost:5000/callback/google'
)

class User(UserMixin):
    def __init__(self, username, role):
        self.username = username
        self.role = role

    def get_id(self):
        return self.username

    def is_admin(self):
        return self.role == 'admin'

@login_manager.user_loader
def load_user(username):
    user_data = db.users.find_one({'username': username})
    if user_data:
        return User(username, user_data.get('role', 'user'))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        admin_key = request.form.get('admin_key')  # Add this field to your form for admin registration
        
        # Check if username or email already exists
        if db.users.find_one({'$or': [{'username': username}, {'email': email}]}):
            flash('Username or email already exists.', 'error')
            return redirect(url_for('register'))
        
        # Verify admin key if role is admin
        if role == 'admin':
            if admin_key != 'Alidiamond10':  # Replace with your actual secret key
                flash('Invalid admin key.', 'error')
                return redirect(url_for('register'))
            else:
                return redirect(url_for('admin_dashboard'))
        
        # Hash the password
        hashed_password = generate_password_hash(password)
        
        # Insert new user into the database
        user_id = db.users.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password,
            'role': role
        }).inserted_id
        
        # Create User object and log in
        user = User(str(user_id), username, role)
        login_user(user)
        
        flash(f'Registration successful! Welcome, {username}! Your role is {role}.', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = db.users.find_one({'username': username})
        if user_data and check_password_hash(user_data['password'], password):
            user = User(username, user_data.get('role', 'user'))
            login_user(user)
            flash('Logged in successfully. Welcome, {} (Role: {})!'.format(user.username, user.role), 'success')
            return redirect(url_for('index'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/login/google')
def login_google():
    authorization_url, state = flow.authorization_url()
    session['state'] = state
    return redirect(authorization_url)

@app.route('/callback/google')
def callback_google():
    flow.fetch_token(authorization_response=request.url)

    if not session['state'] == request.args['state']:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    token_request = requests.Request()

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    email = id_info.get("email")
    name = id_info.get("name")

    # Check if user exists, if not, create a new user
    user = db.users.find_one({'email': email})
    if not user:
        db.users.insert_one({
            'username': email,
            'email': email,
            'name': name,
            'password': None,  # No password for Google-authenticated users
            'role': 'user'  # Default role for new users
        })
    
    user = User(email, user.get('role', 'user') if user else 'user')
    login_user(user)
    flash('Logged in successfully via Google.', 'success')
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/products')
def products():
    products = db.products.find()
    return render_template('products.html', products=products, is_admin=current_user.is_authenticated and current_user.is_admin)

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        image_url = request.form['image_url']  # Add this line
        db.products.insert_one({
            'name': name,
            'description': description,
            'price': price,
            'stock': stock,
            'image_url': image_url  # Add this line
        })
        flash('Product added successfully!', 'success')
        return redirect(url_for('products'))
    return render_template('add_product.html')

# def admin_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if not current_user.is_authenticated or not current_user.is_admin:
#             return jsonify({"success": False, "message": "Admin access required"}), 403
#         return f(*args, **kwargs)
#     return decorated_function

@app.route('/edit_product/<string:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(id):
    product = db.products.find_one({'_id': ObjectId(id)})
    if request.method == 'POST':
        updated_product = {
            'name': request.form['name'],
            'description': request.form['description'],
            'price': float(request.form['price']),
            'stock': int(request.form['stock']),
            'image_url': request.form['image_url']
        }
        db.products.update_one({'_id': ObjectId(id)}, {'$set': updated_product})
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products'))
    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<string:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_product(id):
    print(f"Received delete request for product id: {id}")
    product = db.products.find_one({'_id': ObjectId(id)})
    if product:
        print(f"Found product: {product}")
        result = db.products.delete_one({'_id': ObjectId(id)})
        if result.deleted_count > 0:
            return jsonify({"success": True, "message": "Product deleted successfully"})
        else:
            return jsonify({"success": False, "message": "Failed to delete product"}), 500
    else:
        return jsonify({"success": False, "message": "Product not found"}), 404

@app.route('/add_to_cart/<product_id>')
@login_required
def add_to_cart(product_id):
    product = db.products.find_one({'_id': ObjectId(product_id)})
    if product:
        cart = session.get('cart', {})
        if product_id in cart:
            if cart[product_id] < product['stock']:
                cart[product_id] += 1
                db.products.update_one({'_id': ObjectId(product_id)}, {'$inc': {'stock': -1}})
                flash('Product quantity increased in cart!', 'success')
            else:
                flash('Cannot add more of this item. Stock limit reached!', 'error')
        else:
            if product['stock'] > 0:
                cart[product_id] = 1
                db.products.update_one({'_id': ObjectId(product_id)}, {'$inc': {'stock': -1}})
                flash('Product added to cart!', 'success')
            else:
                flash('Product is out of stock!', 'error')
        session['cart'] = cart
    return redirect(url_for('products'))

@app.route('/cart')
@login_required
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = db.products.find_one({'_id': ObjectId(product_id)})
        if product:
            item_total = product['price'] * quantity
            total += item_total
            cart_items.append({
                'id': str(product['_id']),
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity,
                'item_total': item_total,
                'stock': product['stock'],
                'image_url': product.get('image_url', '')  # Add this line
            })
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/update_cart', methods=['POST'])
@login_required
def update_cart():
    cart = session.get('cart', {})
    product_id = request.form.get('product_id')
    action = request.form.get('action')
    
    if product_id and action:
        product = db.products.find_one({'_id': ObjectId(product_id)})
        if product:
            if action == 'increase':
                if cart.get(product_id, 0) < product['stock']:
                    cart[product_id] = cart.get(product_id, 0) + 1
                    db.products.update_one({'_id': ObjectId(product_id)}, {'$inc': {'stock': -1}})
                else:
                    flash('Cannot add more of this item. Stock limit reached!', 'error')
            elif action == 'decrease':
                if cart.get(product_id, 0) > 1:
                    cart[product_id] -= 1
                    db.products.update_one({'_id': ObjectId(product_id)}, {'$inc': {'stock': 1}})
                else:
                    cart.pop(product_id, None)
                    db.products.update_one({'_id': ObjectId(product_id)}, {'$inc': {'stock': 1}})
            elif action == 'remove':
                quantity = cart.pop(product_id, 0)
                db.products.update_one({'_id': ObjectId(product_id)}, {'$inc': {'stock': quantity}})
    
    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        cart = session.get('cart', {})
        
        # Create an order
        order = {
            'user': current_user.username,
            'items': [],
            'total': 0
        }
        
        for product_id, quantity in cart.items():
            product = db.products.find_one({'_id': ObjectId(product_id)})
            if product:
                item_total = product['price'] * quantity
                order['items'].append({
                    'product_id': product_id,
                    'name': product['name'],
                    'price': product['price'],
                    'quantity': quantity,
                    'item_total': item_total
                })
                order['total'] += item_total
        
        # Insert the order into the database
        db.orders.insert_one(order)
        
        # Clear the cart
        session['cart'] = {}
        
        flash('Order placed successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('checkout.html')

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    total_users = db.users.count_documents({})
    total_products = db.products.count_documents({})
    total_orders = db.orders.count_documents({})
    
    # Calculate total revenue
    orders = db.orders.find()
    total_revenue = sum(order.get('total', 0) for order in orders)
    
    # Get recent activities (you'll need to implement activity logging)
    recent_activities = list(db.activities.find().sort('date', -1).limit(10))
    
    return render_template('admin_dashboard.html',
                           total_users=total_users,
                           total_products=total_products,
                           total_orders=total_orders,
                           total_revenue=total_revenue,
                           recent_activities=recent_activities)

@app.route('/export_reports', methods=['GET', 'POST'])
def export_reports():
    if request.method == 'POST':
        report_type = request.form['report_type']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        file_format = request.form['file_format']
        include_charts = 'include_charts' in request.form
        include_summary = 'include_summary' in request.form

        # Generate the report based on the selected options
        # This is where you'd implement the logic to create the report
        # For example:
        if report_type == 'sales':
            df = generate_sales_report(start_date, end_date)
        elif report_type == 'inventory':
            df = generate_inventory_report()
        # ... handle other report types

        # Save the report in the selected format
        if file_format == 'csv':
            df.to_csv('report.csv', index=False)
            return send_file('report.csv', as_attachment=True)
        elif file_format == 'xlsx':
            df.to_excel('report.xlsx', index=False)
            return send_file('report.xlsx', as_attachment=True)
        elif file_format == 'pdf':
            # You'll need to implement PDF generation
            # This might involve using a library like ReportLab
            pass

    # For GET requests, render the template
    recent_reports = [
        {"name": "Sales Report - June 2023", "date": "2023-07-01", "download_url": "#"},
        {"name": "Inventory Report - Q2 2023", "date": "2023-07-15", "download_url": "#"},
        # Add more recent reports here
    ]
    return render_template('export_reports.html', recent_reports=recent_reports)

@app.route('/manage-users')
@login_required
@admin_required
def manage_users():
    users = list(db.users.find())
    return render_template('manage_users.html', users=users)

@app.route('/api/users', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
@admin_required
def api_users():
    if request.method == 'GET':
        users = list(db.users.find())
        return jsonify([User(user['username'], user['role']).to_dict() for user in users])
    
    elif request.method == 'POST':
        data = request.json
        new_user = {
            'username': data['username'],
            'email': data['email'],
            'password': generate_password_hash(data['password']),
            'role': data['role']
        }
        result = db.users.insert_one(new_user)
        new_user['_id'] = str(result.inserted_id)
        return jsonify(new_user), 201
    
    elif request.method == 'PUT':
        data = request.json
        user = db.users.find_one({'username': data['username']})
        if user:
            update_data = {
                'email': data['email'],
                'role': data['role']
            }
            if 'password' in data:
                update_data['password'] = generate_password_hash(data['password'])
            db.users.update_one({'username': data['username']}, {'$set': update_data})
            return jsonify(User(data['username'], data['role']).to_dict())
        return jsonify({'error': 'User not found'}), 404
    
    elif request.method == 'DELETE':
        username = request.args.get('username')
        result = db.users.delete_one({'username': username})
        if result.deleted_count:
            return '', 204
        return jsonify({'error': 'User not found'}), 404

@app.route('/view_orders')
@login_required
@admin_required
def view_orders():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of orders per page

    try:
        # Get total number of orders
        total_orders = db.orders.count_documents({})

        # Calculate total pages
        total_pages = ceil(total_orders / per_page)

        # Get orders for the current page
        skip = (page - 1) * per_page
        orders = list(db.orders.find().sort('date', -1).skip(skip).limit(per_page))

        # Convert ObjectId to string for each order and format date
        for order in orders:
            order['id'] = str(order.get('_id', ''))
            order.pop('_id', None)
            
            # Handle different date field names and formats
            date_field = order.get('date') or order.get('created_at') or order.get('order_date')
            if isinstance(date_field, datetime):
                order['date'] = date_field.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(date_field, str):
                order['date'] = date_field
            else:
                order['date'] = 'N/A'

            # Ensure all necessary fields are present
            order['customer_name'] = order.get('customer_name', 'N/A')
            order['total'] = order.get('total', 0)
            order['status'] = order.get('status', 'Unknown')

        # Count pending and completed orders
        pending_orders = db.orders.count_documents({'status': 'Pending'})
        completed_orders = db.orders.count_documents({'status': 'Completed'})

        return render_template('view_orders.html', 
                               orders=orders, 
                               total_orders=total_orders,
                               pending_orders=pending_orders,
                               completed_orders=completed_orders,
                               page=page,
                               total_pages=total_pages)

    except Exception as e:
        # Log the error
        app.logger.error(f"Error in view_orders: {str(e)}")
        # Return an error page or message
        return render_template('error.html', message="An error occurred while fetching orders."), 500

@app.route('/api/order/<order_id>', methods=['GET'])
@login_required
@admin_required
def get_order_details(order_id):
    order = db.orders.find_one({'_id': ObjectId(order_id)})
    if order:
        order['id'] = str(order['_id'])
        del order['_id']
        order['date'] = order['date'].strftime('%Y-%m-%d %H:%M:%S')
        return jsonify(order)
    return jsonify({'error': 'Order not found'}), 404

@app.route('/api/order/<order_id>/status', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    new_status = request.json.get('status')
    if not new_status:
        return jsonify({'success': False, 'error': 'No status provided'}), 400
    
    try:
        result = db.orders.update_one({'_id': ObjectId(order_id)}, {'$set': {'status': new_status}})
        if result.modified_count > 0:
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Order not found or status not changed'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500   

if __name__ == '__main__':
    app.run(debug=True)