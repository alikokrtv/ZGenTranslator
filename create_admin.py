"""
Admin hesabı oluşturma veya mevcut hesabı admin yapma script'i
"""
import sqlite3
import hashlib
import os

# Veritabanı bağlantısı
DB_PATH = os.path.join(os.path.dirname(__file__), 'zgen_translator.db')

def get_db_connection():
    """Veritabanı bağlantısı oluştur"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_admin_user(username, email, password):
    """Yeni bir admin kullanıcı oluştur"""
    # Şifreyi hash'le
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Önce kullanıcının var olup olmadığını kontrol et
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
        existing_user = cursor.fetchone()
        
        if existing_user:
            user_id = existing_user['id']
            print(f"Kullanıcı zaten mevcut (ID: {user_id}). Admin yetkisi veriliyor...")
            cursor.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (user_id,))
            conn.commit()
            print(f"'{username}' kullanıcısına admin yetkisi verildi!")
            return
        
        # Yeni admin kullanıcı oluştur
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, is_admin)
            VALUES (?, ?, ?, 1)
        """, (username, email, password_hash))
        
        conn.commit()
        print(f"Yeni admin kullanıcı '{username}' başarıyla oluşturuldu!")
    except Exception as e:
        print(f"Hata oluştu: {e}")
    finally:
        conn.close()

def list_all_users():
    """Tüm kullanıcıları listele"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, username, email, is_admin FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("Veritabanında henüz kullanıcı bulunmuyor.")
            return
        
        print("\nKullanıcı Listesi:")
        print("-" * 60)
        print(f"{'ID':<5} {'Kullanıcı Adı':<20} {'E-posta':<30} {'Admin'}")
        print("-" * 60)
        
        for user in users:
            is_admin = "Evet" if user['is_admin'] == 1 else "Hayır"
            print(f"{user['id']:<5} {user['username']:<20} {user['email']:<30} {is_admin}")
    except Exception as e:
        print(f"Hata oluştu: {e}")
    finally:
        conn.close()

def make_user_admin(user_id):
    """Kullanıcıyı admin yap"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            print(f"ID: {user_id} olan kullanıcı bulunamadı.")
            return
        
        cursor.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (user_id,))
        conn.commit()
        print(f"'{user['username']}' kullanıcısına admin yetkisi verildi!")
    except Exception as e:
        print(f"Hata oluştu: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Z Kuşağı Translator - Admin Yönetimi")
    print("=" * 40)
    
    while True:
        print("\nİşlem Seçin:")
        print("1. Yeni admin kullanıcı oluştur")
        print("2. Mevcut kullanıcıları listele")
        print("3. Mevcut kullanıcıyı admin yap")
        print("4. Çıkış")
        
        choice = input("\nSeçiminiz (1-4): ")
        
        if choice == "1":
            username = input("Kullanıcı adı: ")
            email = input("E-posta: ")
            password = input("Şifre: ")
            create_admin_user(username, email, password)
        
        elif choice == "2":
            list_all_users()
        
        elif choice == "3":
            list_all_users()
            user_id = input("\nAdmin yapmak istediğiniz kullanıcının ID'si: ")
            make_user_admin(int(user_id))
        
        elif choice == "4":
            print("Programdan çıkılıyor...")
            break
        
        else:
            print("Geçersiz seçim! Lütfen 1-4 arasında bir sayı girin.")
