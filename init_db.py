"""
Database initialization script for Car Leasing Application.
Creates tables and seeds sample data.
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

# Database path
DB_PATH = os.path.join('database', 'leasing.db')

def init_database():
    """Create database tables and seed initial data."""
    
    # Create database directory if it doesn't exist
    os.makedirs('database', exist_ok=True)
    
    # Connect to database (creates file if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student', 'staff'))
        )
    ''')
    
    # Create cars table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            image TEXT
        )
    ''')
    
    # Create applications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            car_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (car_id) REFERENCES cars(id)
        )
    ''')
    
    # Clear existing data (for clean initialization)
    cursor.execute('DELETE FROM applications')
    cursor.execute('DELETE FROM cars')
    cursor.execute('DELETE FROM users')
    
    # Seed users
    # Student user
    student_password = generate_password_hash('student123')
    cursor.execute('''
        INSERT INTO users (email, password, role)
        VALUES (?, ?, ?)
    ''', ('student@example.com', student_password, 'student'))
    
    # Staff user
    staff_password = generate_password_hash('staff123')
    cursor.execute('''
        INSERT INTO users (email, password, role)
        VALUES (?, ?, ?)
    ''', ('staff@example.com', staff_password, 'staff'))
    
    # Seed cars (4-6 sample cars)
    cars_data = [
        ('Toyota Camry 2024', 299.99, 'Reliable sedan perfect for daily commuting. Features modern safety technology and excellent fuel economy.', 'static/img/camry.jpg'),
        ('Honda Civic 2024', 279.99, 'Compact and efficient, ideal for city driving. Great value with advanced features.', 'static/img/civic.jpg'),
        ('Ford Mustang 2024', 499.99, 'Sporty and powerful muscle car. Perfect for those who love performance and style.', 'static/img/mustang.jpg'),
        ('Tesla Model 3', 599.99, 'Electric vehicle with cutting-edge technology. Zero emissions and autopilot features.', 'static/img/tesla.jpg'),
        ('BMW 3 Series', 549.99, 'Luxury sedan with premium features. Comfortable ride with excellent handling.', 'static/img/bmw.jpg'),
        ('Nissan Altima 2024', 269.99, 'Spacious and comfortable mid-size sedan. Great for long trips and family use.', 'static/img/altima.jpg')
    ]
    
    cursor.executemany('''
        INSERT INTO cars (model, price, description, image)
        VALUES (?, ?, ?, ?)
    ''', cars_data)
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"Database initialized successfully at {DB_PATH}")
    print("Created tables: users, cars, applications")
    print("Seeded data: 1 student, 1 staff, 6 cars")
    print("\nLogin credentials:")
    print("Student: student@example.com / student123")
    print("Staff: staff@example.com / staff123")

if __name__ == '__main__':
    init_database()

