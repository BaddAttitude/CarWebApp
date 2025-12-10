"""
Flask Car Leasing Application
Main application file with all routes and business logic.
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from werkzeug.security import check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Change in production!

# Database path
DB_PATH = os.path.join('database', 'leasing.db')

def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    """Decorator to require specific role for routes."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login to access this page.', 'warning')
                return redirect(url_for('index'))
            if session.get('role') != role:
                flash('Access denied. Insufficient permissions.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Home route
@app.route('/')
def index():
    """Homepage with links to login pages."""
    return render_template('index.html')

# Student login routes
@app.route('/login_student', methods=['GET', 'POST'])
def login_student():
    """Handle student login (GET shows form, POST processes login)."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password.', 'danger')
            return render_template('login_student.html')
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE email = ? AND role = ?',
            (email, 'student')
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['role'] = user['role']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard_student'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login_student.html')

# Staff login routes
@app.route('/login_staff', methods=['GET', 'POST'])
def login_staff():
    """Handle staff login (GET shows form, POST processes login)."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password.', 'danger')
            return render_template('login_staff.html')
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE email = ? AND role = ?',
            (email, 'staff')
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['role'] = user['role']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard_staff'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login_staff.html')

# Student dashboard
@app.route('/dashboard_student')
@login_required
@role_required('student')
def dashboard_student():
    """Student dashboard showing cars and their applications."""
    conn = get_db_connection()
    
    # Get all cars
    cars = conn.execute('SELECT * FROM cars ORDER BY id').fetchall()
    
    # Get student's applications with car details
    applications = conn.execute('''
        SELECT a.*, c.model, c.price, c.image
        FROM applications a
        JOIN cars c ON a.car_id = c.id
        WHERE a.user_id = ?
        ORDER BY a.date DESC
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    return render_template('dashboard_student.html', cars=cars, applications=applications)

# Staff dashboard
@app.route('/dashboard_staff')
@login_required
@role_required('staff')
def dashboard_staff():
    """Staff dashboard showing cars and all applications."""
    conn = get_db_connection()
    
    # Get all cars
    cars = conn.execute('SELECT * FROM cars ORDER BY id').fetchall()
    
    # Get all applications with user and car details
    applications = conn.execute('''
        SELECT a.*, c.model, c.price, c.image, u.email as user_email
        FROM applications a
        JOIN cars c ON a.car_id = c.id
        JOIN users u ON a.user_id = u.id
        ORDER BY a.date DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard_staff.html', cars=cars, applications=applications)

# Cars listing page
@app.route('/cars')
@login_required
def cars():
    """Display all available cars."""
    conn = get_db_connection()
    cars = conn.execute('SELECT * FROM cars ORDER BY id').fetchall()
    conn.close()
    return render_template('cars.html', cars=cars)

# Car detail page
@app.route('/car/<int:id>')
@login_required
def car_detail(id):
    """Display details of a specific car."""
    conn = get_db_connection()
    car = conn.execute('SELECT * FROM cars WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if not car:
        flash('Car not found.', 'danger')
        return redirect(url_for('cars'))
    
    return render_template('car_detail.html', car=car)

# Application routes
@app.route('/apply/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('student')
def apply(id):
    """Handle lease application (GET shows form, POST processes application)."""
    conn = get_db_connection()
    car = conn.execute('SELECT * FROM cars WHERE id = ?', (id,)).fetchone()
    
    if not car:
        conn.close()
        flash('Car not found.', 'danger')
        return redirect(url_for('cars'))
    
    if request.method == 'POST':
        # Check if user already applied for this car (optional - can allow multiple)
        # For simplicity, we'll allow multiple applications
        
        from datetime import datetime
        application_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        conn.execute('''
            INSERT INTO applications (user_id, car_id, date)
            VALUES (?, ?, ?)
        ''', (session['user_id'], id, application_date))
        
        conn.commit()
        conn.close()
        
        flash(f'Application submitted successfully for {car["model"]}!', 'success')
        return redirect(url_for('dashboard_student'))
    
    conn.close()
    return render_template('apply.html', car=car)

# Profile page
@app.route('/profile')
@login_required
def profile():
    """Display user profile information."""
    return render_template('profile.html')

# Payments page
@app.route('/payments')
@login_required
def payments():
    """Display payments page with dummy data."""
    # Static dummy payment data
    payments = [
        {'id': 1, 'car': 'Toyota Camry 2024', 'amount': 299.99, 'date': '2024-01-15', 'status': 'Paid'},
        {'id': 2, 'car': 'Honda Civic 2024', 'amount': 279.99, 'date': '2024-02-15', 'status': 'Paid'},
        {'id': 3, 'car': 'Ford Mustang 2024', 'amount': 499.99, 'date': '2024-03-15', 'status': 'Pending'},
    ]
    return render_template('payments.html', payments=payments)

# Logout route
@app.route('/logout')
def logout():
    """Logout user and clear session."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

# API endpoint for cars (JSON)
@app.route('/api/cars')
def api_cars():
    """Return all cars as JSON."""
    conn = get_db_connection()
    cars = conn.execute('SELECT * FROM cars ORDER BY id').fetchall()
    conn.close()
    
    # Convert rows to dictionaries
    cars_list = [dict(car) for car in cars]
    return jsonify(cars_list)

if __name__ == '__main__':
    # Ensure database exists
    if not os.path.exists(DB_PATH):
        print("Database not found. Please run init_db.py first.")
    else:
        app.run(debug=True, host='0.0.0.0', port=5000)

