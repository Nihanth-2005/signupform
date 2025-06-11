from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'vlnworkspace'
}

# Create database connection
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

# Create users table if not exists
def create_users_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            date_of_birth DATE NOT NULL,
            country_code VARCHAR(5) NOT NULL,
            phone_number VARCHAR(20) NOT NULL,
            gender VARCHAR(10) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# Initialize the database
create_users_table()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        flash('Login successful!', 'success')
        return redirect(url_for('welcome'))
    else:
        flash('Invalid email or password', 'danger')
        return redirect(url_for('login'))

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    # Get form data
    full_name = request.form.get('full_name')
    dob = request.form.get('dob')
    country_code = request.form.get('country_code')
    phone = request.form.get('phone')
    gender = request.form.get('gender')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    # Validate inputs
    errors = []
    if not full_name:
        errors.append('Full name is required')
    if not dob:
        errors.append('Date of birth is required')
    if not phone:
        errors.append('Phone number is required')
    if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        errors.append('Valid email is required')
    if len(password) < 8:
        errors.append('Password must be at least 8 characters')
    if password != confirm_password:
        errors.append('Passwords do not match')
    
    if errors:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('signup'))
    
    # Check if email already exists
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
    if cursor.fetchone():
        flash('Email address already exists', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('signup'))
    
    # Hash password and save user
    hashed_password = generate_password_hash(password)
    try:
        cursor.execute('''
            INSERT INTO users (full_name, date_of_birth, country_code, phone_number, gender, email, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (full_name, dob, country_code, phone, gender, email, hashed_password))
        conn.commit()
        flash('Account created successfully! Please login', 'success')
        return redirect(url_for('login'))
    except Exception as e:
        flash(f'Error creating account: {str(e)}', 'danger')
        return redirect(url_for('signup'))
    finally:
        cursor.close()
        conn.close()

@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

if __name__ == '__main__':
    app.run(debug=True)