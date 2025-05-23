import hashlib
import sqlite3
import os

def create_test_user():
    """Create a test user in the database for login testing"""
    print("Creating test user...")
    
    # Database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zgen_translator.db')
    print(f"Database path: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if test user already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", ("testuser",))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"Test user already exists with ID: {existing_user['id']}")
            conn.close()
            return
        
        # Create test user credentials
        username = "testuser"
        password = "testpassword"
        email = "test@example.com"
        
        # Hash the password (same method as in the app)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Insert the user
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, is_admin)
            VALUES (?, ?, ?, ?)
        """, (username, email, password_hash, 1))  # Set as admin for testing all features
        
        user_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        print(f"✅ Test user created successfully!")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"User ID: {user_id}")
        print(f"Admin: Yes")
        
    except Exception as e:
        print(f"❌ Error creating test user: {str(e)}")

if __name__ == "__main__":
    create_test_user() 