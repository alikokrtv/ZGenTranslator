import os
import logging
from datetime import datetime
from db_config import get_db_connection

# Logging ayarları
logger = logging.getLogger('models')

# Veritabanı tipi kontrolü ve parametre işaretleyici belirleme
def get_param_placeholder(conn):
    """
    Veritabanı bağlantı tipine göre doğru parametre işaretleyicisini döndür
    SQLite için ? ve PostgreSQL için %s
    """
    # Bağlantı tipine göre doğru işaretleyiciyi belirle
    if hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn)):
        return '%s'  # PostgreSQL bağlantısı
    else:
        return '?'  # SQLite bağlantısı

# get_db_connection fonksiyonu artık db_config.py'de

def init_db():
    """Initialize the database with tables if they don't exist"""
    import logging
    logger = logging.getLogger('models')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Veritabanı tipini kontrol et
    is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
    
    try:
        logger.info(f"{'PostgreSQL' if is_postgres else 'SQLite'} için tablolar oluşturuluyor...")
        
        # PostgreSQL için farklı PRIMARY KEY sözdizimi 
        if is_postgres:
            # PostgreSQL için tablo oluşturma - ÖNCE users tablosunu oluştur
            logger.info("PostgreSQL için tablolar oluşturuluyor... Önce users tablosu.")
            
            # Önce users tablosunu oluştur
            try:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    role TEXT DEFAULT 'user',
                    is_active BOOLEAN DEFAULT TRUE,
                    points INTEGER DEFAULT 0
                )
                """)
                conn.commit()
                logger.info("PostgreSQL users tablosu başarıyla oluşturuldu.")
            except Exception as e:
                logger.error(f"PostgreSQL users tablosu oluşturulurken hata: {e}")
                conn.rollback()
            
            # Sonra words tablosunu oluştur (users'a foreign key içeriyor)
            try:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS words (
                    id SERIAL PRIMARY KEY,
                    word TEXT NOT NULL,
                    meaning TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    suggested_by INTEGER,
                    votes_up INTEGER DEFAULT 0,
                    votes_down INTEGER DEFAULT 0,
                    is_approved INTEGER DEFAULT 0,
                    approved_by INTEGER,
                    approved_at TIMESTAMP,
                    FOREIGN KEY (suggested_by) REFERENCES users(id) ON DELETE SET NULL,
                    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL
                )
                """)
                conn.commit()
                logger.info("PostgreSQL words tablosu başarıyla oluşturuldu.")
            except Exception as e:
                logger.error(f"PostgreSQL words tablosu oluşturulurken hata: {e}")
                conn.rollback()
            
            # Create suggestions table for pending words
            cur.execute("""
            CREATE TABLE IF NOT EXISTS suggestions (
                id SERIAL PRIMARY KEY,
                word TEXT NOT NULL,
                meaning TEXT NOT NULL,
                suggested_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                admin_notes TEXT,
                FOREIGN KEY (suggested_by) REFERENCES users(id) ON DELETE SET NULL
            )
            """)
            
            # Create edit requests table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS edit_requests (
                id SERIAL PRIMARY KEY,
                word_id INTEGER NOT NULL,
                new_meaning TEXT NOT NULL,
                reason TEXT,
                requested_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                admin_notes TEXT,
                FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE,
                FOREIGN KEY (requested_by) REFERENCES users(id) ON DELETE SET NULL
            )
            """)
            
            # Create users table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                contribution_count INTEGER DEFAULT 0,
                bio TEXT,
                is_admin INTEGER DEFAULT 0
            )
            """)
            
            # Create achievements table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT NOT NULL,
                icon TEXT NOT NULL,
                requirement_count INTEGER NOT NULL
            )
            """)
            
            # Create user achievements junction table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                user_id INTEGER,
                achievement_id INTEGER,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, achievement_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE
            )
            """)
            
        else:
            # SQLite için tablo oluşturma
            logger.info("SQLite için tablolar oluşturuluyor...")
            
            # Create words table
            cur.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                meaning TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                suggested_by INTEGER,
                votes_up INTEGER DEFAULT 0,
                votes_down INTEGER DEFAULT 0,
                is_approved INTEGER DEFAULT 0,
                approved_by INTEGER,
                approved_at TIMESTAMP,
                FOREIGN KEY (suggested_by) REFERENCES users(id),
                FOREIGN KEY (approved_by) REFERENCES users(id)
            )
            ''')
            
            # Create suggestions table for pending words
            cur.execute('''
            CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                meaning TEXT NOT NULL,
                suggested_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                admin_notes TEXT,
                FOREIGN KEY (suggested_by) REFERENCES users(id)
            )
            ''')
            
            # Create edit requests table
            cur.execute('''
            CREATE TABLE IF NOT EXISTS edit_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER NOT NULL,
                new_meaning TEXT NOT NULL,
                reason TEXT,
                requested_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                admin_notes TEXT,
                FOREIGN KEY (word_id) REFERENCES words(id),
                FOREIGN KEY (requested_by) REFERENCES users(id)
            )
            ''')
            
            # Create users table
            cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                contribution_count INTEGER DEFAULT 0,
                bio TEXT,
                is_admin INTEGER DEFAULT 0
            )
            ''')
            
            # Create achievements table
            cur.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT NOT NULL,
                icon TEXT NOT NULL,
                requirement_count INTEGER NOT NULL
            )
            ''')
            
            # Create user achievements junction table
            cur.execute('''
            CREATE TABLE IF NOT EXISTS user_achievements (
                user_id INTEGER,
                achievement_id INTEGER,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, achievement_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (achievement_id) REFERENCES achievements(id)
            )
            ''')
            
            # Create password reset tokens table
            cur.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                used INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            ''')
        
        conn.commit()
        logger.info("Veritabanı tabloları başarıyla oluşturuldu.")
        
    except Exception as e:
        conn.rollback() if hasattr(conn, 'rollback') else None
        logger.error(f"Veritabanı oluşturma hatası: {str(e)}")
        print(f"Veritabanı oluşturma hatası: {str(e)}")
        raise
    finally:
        conn.close()
    
    # Seed initial words after creating tables
    # Veritabanı tabloları oluşturulduktan sonra başlangıç kelimelerini ekle
    seed_initial_words()
    
    # Seed initial achievements
    seed_initial_achievements()

def seed_initial_words():
    """Veritabanına başlangıç Z kuşağı kelimelerini ekle"""
    # Z kuşağı için başlangıç kelime listesi
    initial_words = {
        "güno": "Günaydın",
        "ajg": "Aynen ya, çok iyi",
        "vibe": "Ortam, hava, enerji",
        "sus": "Şüpheli, güvenilmez",
        "fr": "Cidden, gerçekten (for real)",
        "no cap": "Yalan değil, cidden",
        "cringe": "Utanç verici, rahatsız edici",
        "yeet": "Bir şeyi güçlü atmak veya reddetmek",
        "flex": "Hava atmak, gösteriş yapmak",
        "slay": "Çok iyi yapmak, başarılı olmak",
        "ok boomer": "Eski kafalı düşüncelere karşı bir ifade",
        "lit": "Harika, mükemmel",
        "savage": "Acımasız, sert ama havalı",
        "stan": "Fanatik hayran olmak",
        "rizz": "Karşı cinsi etkileme yeteneği",
        "npc": "Sıradan, düşünemeyen insan (non-player character)",
        "gg": "İyi oyun, tebrikler (good game)",
        "bruh": "Abi, dostum (şaşkınlık ifadesi)",
        "ship": "İki kişinin ilişkide olmasını istemek",
        "based": "Kendinden emin, korkmadan fikrini söyleyen"
    }
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Veritabanında kelime olup olmadığını kontrol et
        cur.execute("SELECT COUNT(*) FROM words")
        count = cur.fetchone()[0]
        
        # Eğer veritabanı boş ise, başlangıç kelimelerini ekle
        if count == 0:
            logger.info("Veritabanı boş, başlangıç Z kuşağı kelimelerini ekliyorum...")
            
            # Veritabanı tipini kontrol et
            is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
            param_placeholder = '%s' if is_postgres else '?'
            
            for word, meaning in initial_words.items():
                current_time = datetime.now()
                try:
                    query = f"INSERT INTO words (word, meaning, is_approved, approved_at) VALUES ({param_placeholder}, {param_placeholder}, 1, {param_placeholder})"
                    cur.execute(query, (word, meaning, current_time))
                except Exception as e:
                    logger.error(f"Kelime eklerken hata: {e}")
            
            conn.commit()
            logger.info(f"{len(initial_words)} kelime veritabanına eklendi.")
        else:
            logger.info(f"Veritabanında zaten {count} kelime var, yeni kelime eklemiyorum.")
            
            # Mevcut kelimelerin onaylı olduğundan emin ol
            try:
                cur.execute("UPDATE words SET is_approved = 1, approved_at = CURRENT_TIMESTAMP WHERE is_approved = 0 OR is_approved IS NULL")
                updated_count = cur.rowcount
                if updated_count > 0:
                    logger.info(f"{updated_count} kelime onaylı olarak işaretlendi.")
            except Exception as e:
                logger.error(f"Kelimeleri onaylı olarak işaretlerken hata: {e}")
        
    except Exception as e:
        logger.error(f"seed_initial_words fonksiyonunda hata: {e}")
        conn.rollback()
    finally:
        conn.close()

def get_word(word):
    """Get a word's meanings from the database (can return multiple)"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Veritabanı tipini kontrol et
    is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
    param_placeholder = get_param_placeholder(conn)
    
    # Veritabanı tipine göre farklı sorgu kullan
    if is_postgres:
        # PostgreSQL için ILIKE kullan (case-insensitive eşleşme)
        query = f"""
            SELECT w.*, u.username as suggested_by_username
            FROM words w
            LEFT JOIN users u ON w.suggested_by = u.id
            WHERE w.word ILIKE {param_placeholder} AND w.is_approved = 1
            ORDER BY w.votes_up DESC
        """
    else:
        # SQLite için COLLATE NOCASE kullan
        query = f"""
            SELECT w.*, u.username as suggested_by_username
            FROM words w
            LEFT JOIN users u ON w.suggested_by = u.id
            WHERE w.word = {param_placeholder} COLLATE NOCASE AND w.is_approved = 1
            ORDER BY w.votes_up DESC
        """
    
    cur.execute(query, (word,))
    
    results = cur.fetchall()
    
    conn.close()
    return [dict(result) for result in results] if results else None

def add_word(word, meaning, suggested_by=None):
    """Add a new word to the database as a suggestion (pending approval)"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Veritabanı tipini kontrol et
    is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
    param_placeholder = '%s' if is_postgres else '?'
    
    try:
        # Instead of directly adding to words table, add to suggestions
        query = f"INSERT INTO suggestions (word, meaning, suggested_by, status) VALUES ({param_placeholder}, {param_placeholder}, {param_placeholder}, {param_placeholder})"
        
        if is_postgres:
            query += " RETURNING id"
            cur.execute(query, (word.lower(), meaning, suggested_by, 'pending'))
            suggestion_id = cur.fetchone()[0]  # PostgreSQL'de RETURNING kullanarak ID al
        else:
            cur.execute(query, (word.lower(), meaning, suggested_by, 'pending'))
            # Veritabanı tipine göre ID al
            if is_postgres:
                cur.execute("SELECT lastval()")
                suggestion_id = cur.fetchone()[0]
            else:
                suggestion_id = cur.lastrowid  # SQLite için
        
        conn.commit()
        return suggestion_id
    except Exception as e:
        logger.error(f"Error adding word suggestion: {e}")
        conn.rollback() if hasattr(conn, 'rollback') else None
        return None
    finally:
        conn.close()

def approve_word(suggestion_id, admin_id):
    """Approve a word suggestion and add it to the words table"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Veritabanı tipini kontrol et
    is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
    param_placeholder = '%s' if is_postgres else '?'
    
    try:
        # Get the suggestion
        query = f"SELECT * FROM suggestions WHERE id = {param_placeholder}"
        cur.execute(query, (suggestion_id,))
        suggestion = cur.fetchone()
        
        if not suggestion:
            return False, "Öneri bulunamadı"
        
        # PostgreSQL için sonuç işleme
        if is_postgres and not isinstance(suggestion, dict):
            columns = ['id', 'word', 'meaning', 'suggested_by', 'created_at', 'status', 'admin_notes']
            suggestion_dict = {}
            for i, col in enumerate(columns):
                suggestion_dict[col] = suggestion[i]
            suggestion = suggestion_dict
        
        # Add the word to the words table
        insert_query = f"""
            INSERT INTO words 
            (word, meaning, suggested_by, is_approved, approved_by, approved_at) 
            VALUES ({param_placeholder}, {param_placeholder}, {param_placeholder}, 1, {param_placeholder}, CURRENT_TIMESTAMP)
        """
        
        if is_postgres:
            insert_query += " RETURNING id"
            cur.execute(insert_query, (suggestion['word'], suggestion['meaning'], suggestion['suggested_by'], admin_id))
            word_id = cur.fetchone()[0]
        else:
            cur.execute(insert_query, (suggestion['word'], suggestion['meaning'], suggestion['suggested_by'], admin_id))
            # Veritabanı tipine göre ID al
            if is_postgres:
                cur.execute("SELECT lastval()")
                word_id = cur.fetchone()[0]
            else:
                word_id = cur.lastrowid  # SQLite için
        
        # Update suggestion status
        update_query = f"UPDATE suggestions SET status = 'approved' WHERE id = {param_placeholder}"
        cur.execute(update_query, (suggestion_id,))
        
        # Update user's contribution count if user exists
        if suggestion['suggested_by']:
            contribution_query = f"UPDATE users SET contribution_count = contribution_count + 1 WHERE id = {param_placeholder}"
            cur.execute(contribution_query, (suggestion['suggested_by'],))
            # Check if user earned any achievements
            check_user_achievements(conn, suggestion['suggested_by'])
        
        conn.commit()
        conn.close()
        return True, word_id
    except Exception as e:
        print(f"Error approving word: {e}")
        conn.close()
        return False, str(e)

def reject_word(suggestion_id, admin_id, admin_notes=None):
    """Reject a word suggestion"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Veritabanı tipini kontrol et
    is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
    param_placeholder = '%s' if is_postgres else '?'
    
    try:
        # Update suggestion status
        query = f"UPDATE suggestions SET status = 'rejected', admin_notes = {param_placeholder} WHERE id = {param_placeholder}"
        cur.execute(query, (admin_notes, suggestion_id))
        
        conn.commit()
        return True, "Öneri başarıyla reddedildi"
    except Exception as e:
        logger.error(f"Error rejecting word: {e}")
        conn.rollback() if hasattr(conn, 'rollback') else None
        return False, str(e)
    finally:
        conn.close()


# Şifre sıfırlama fonksiyonları
def generate_reset_token(user_id):
    """Generate a unique token for password reset"""
    import secrets
    import datetime
    
    token = secrets.token_urlsafe(32)  # 32 byte güvenli token oluştur
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Veritabanı tipini kontrol et
    is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
    param_placeholder = '%s' if is_postgres else '?'
    
    try:
        # Token'in süresi 24 saat
        expires_at = datetime.datetime.now() + datetime.timedelta(hours=24)
        
        # Token'i veritabanına kaydet
        query = f"INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES ({param_placeholder}, {param_placeholder}, {param_placeholder})"
        
        if is_postgres:
            query += " RETURNING id"
            cur.execute(query, (user_id, token, expires_at))
        else:
            cur.execute(query, (user_id, token, expires_at))
        
        conn.commit()
        return token
    except Exception as e:
        logger.error(f"Error generating reset token: {e}")
        conn.rollback() if hasattr(conn, 'rollback') else None
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    """Get user by email"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Veritabanı tipini kontrol et
    is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
    param_placeholder = '%s' if is_postgres else '?'
    
    try:
        if is_postgres:
            # PostgreSQL için case-insensitive sorgu (ILIKE kullan)
            query = "SELECT * FROM users WHERE email ILIKE %s"
            cur.execute(query, (email,))
        else:
            # SQLite için case-insensitive sorgu (COLLATE NOCASE kullan)
            query = "SELECT * FROM users WHERE email = ? COLLATE NOCASE"
            cur.execute(query, (email,))
            
        user = cur.fetchone()
            
        # SQLite sonucunu sözlüğe çevir
        if user and not isinstance(user, dict):
            columns = ['id', 'username', 'email', 'password_hash', 'created_at', 
                      'updated_at', 'contribution_count', 'bio', 'is_admin']
            user = dict(zip(columns, user))
        
        return user
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        return None
    finally:
        conn.close()

def verify_reset_token(token):
    """Verify if a reset token is valid"""
    import datetime
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Veritabanı tipini kontrol et
    is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
    param_placeholder = '%s' if is_postgres else '?'
    
    try:
        query = f"""SELECT t.*, u.email, u.username FROM password_reset_tokens t 
                JOIN users u ON t.user_id = u.id 
                WHERE t.token = {param_placeholder} AND t.used = 0"""
        
        cur.execute(query, (token,))
        result = cur.fetchone()
        
        if not result:
            return None, "Geçersiz veya kullanılmış token"
        
        # PostgreSQL ve SQLite sonuçlarını işleme
        if not isinstance(result, dict):
            # Tuple sonucunu sözlüğe çevir
            columns = ['id', 'user_id', 'token', 'created_at', 'expires_at', 'used', 'email', 'username']
            result_dict = {}
            for i, col in enumerate(columns):
                if i < len(result):
                    result_dict[col] = result[i]
            result = result_dict
        
        # Tokenin süresi dolmuş mu kontrol et
        now = datetime.datetime.now()
        
        # expires_at string veya datetime olabilir
        try:
            if isinstance(result['expires_at'], str):
                expires_at = datetime.datetime.fromisoformat(result['expires_at'].replace(' ', 'T'))
            else:
                expires_at = result['expires_at']
                
            if now > expires_at:
                return None, "Tokenin süresi dolmuş"
        except Exception as e:
            logger.error(f"Token süresi kontrol edilirken hata: {e}")
            return None, "Token süresi kontrol edilirken hata oluştu"
        
        # Token geçerli, kullanıcı bilgilerini döndür
        token_data = {
            'user_id': result['user_id'],
            'email': result['email'],
            'username': result['username'],
            'token': token
        }
        
        return token_data, "Token geçerli"
    except Exception as e:
        logger.error(f"Token doğrulanırken hata: {e}")
        return None, f"Token doğrulanırken hata oluştu: {str(e)}"
    finally:
        conn.close()

def reset_password(token, new_password):
    """Reset password using a valid token"""
    import hashlib
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Veritabanı tipini kontrol et
    is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
    param_placeholder = '%s' if is_postgres else '?'
    
    try:
        # Token'i doğrula
        token_data, message = verify_reset_token(token)
        
        if not token_data:
            return False, message
        
        # Şifreyi güncelle
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        update_query = f"UPDATE users SET password_hash = {param_placeholder} WHERE id = {param_placeholder}"
        cur.execute(update_query, (password_hash, token_data['user_id']))
        
        # Token'i kullanıldı olarak işaretle
        token_query = f"UPDATE password_reset_tokens SET used = 1 WHERE token = {param_placeholder}"
        cur.execute(token_query, (token,))
        
        conn.commit()
        return True, "Şifre başarıyla sıfırlandı"
    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        conn.rollback() if hasattr(conn, 'rollback') else None
        return False, str(e)
    finally:
        conn.close()

def add_suggestion(word, meaning, suggested_by=None):
    """Add a new word suggestion to the database"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Veritabanı tipini kontrol et
    is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
    param_placeholder = '%s' if is_postgres else '?'
    
    try:
        query = f"INSERT INTO suggestions (word, meaning, suggested_by) VALUES ({param_placeholder}, {param_placeholder}, {param_placeholder})"
        cur.execute(query, (word.lower(), meaning, suggested_by))
        conn.commit()
        return True, "Öneri başarıyla kaydedildi"
    except Exception as e:
        logger.error(f"Error adding suggestion: {e}")
        conn.rollback() if hasattr(conn, 'rollback') else None
        return False, str(e)
    finally:
        conn.close()

def get_popular_words(limit):
    """Get a list of popular words from the database"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Veritabanı tipini kontrol et
        is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
        param_placeholder = get_param_placeholder(conn)
        
        # Basitleştirilmiş sorgu - sadece temel bilgileri getirelim
        query = f"""
            SELECT id, word, meaning 
            FROM words
            ORDER BY votes_up DESC, created_at DESC
            LIMIT {param_placeholder}
        """
        
        cur.execute(query, (limit,))
        
        # Sonuçları basit sözlük listesi olarak döndür
        words = []
        if is_postgres:
            # PostgreSQL sonuçları zaten sözlük olarak döner
            words = [dict(row) for row in cur.fetchall()]
        else:
            # SQLite için tuple'dan sözlüğe çevir
            for row in cur.fetchall():
                word = {
                    'id': row[0],
                    'word': row[1],
                    'meaning': row[2]
                }
                words.append(word)
        
        logger.info(f"Popüler kelimeler: {len(words)} adet") 
        return words
        
    except Exception as e:
        import traceback
        logger.error(f"Popüler kelimeler getirilirken hata: {e}")
        logger.error(traceback.format_exc())
        return []
    finally:
        if 'conn' in locals():
            conn.close()

def seed_initial_achievements():
    """Seed the database with initial achievements"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Veritabanı tipini kontrol et
    is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
    param_placeholder = '%s' if is_postgres else '?'
    
    try:
        # Check if achievements already exist
        cur.execute("SELECT COUNT(*) FROM achievements")
        count_result = cur.fetchone()
        
        # PostgreSQL ile SQLite sonuçları farklı formatta olabilir
        count = count_result[0] if isinstance(count_result, tuple) else count_result
        
        if count == 0:
            logger.info("Başarımları veritabanına ekliyorum...")
            achievements = [
                ("Yeni Çevirmen", "İlk kelimeni ekledin!", "📝", 1),
                ("Kelime Ustası", "10 kelime ekledin", "🔤", 10),
                ("Z Kuşağı Çevirmeni", "25 kelime ekledin", "💬", 25),
                ("Dil Dehası", "50 kelime ekledin", "🏆", 50),
                ("Z-Sözlük Oluşturucu", "100 kelime ekledin", "👑", 100)
            ]
            
            # PostgreSQL için parametre yerleştirici uyumlu sorgu oluştur
            query = f"""
                INSERT INTO achievements (name, description, icon, requirement_count)
                VALUES ({param_placeholder}, {param_placeholder}, {param_placeholder}, {param_placeholder})
            """
            
            # Her bir başarımı tek tek ekle (executemany PostgreSQL'de sorun çıkarabilir)
            for achievement in achievements:
                cur.execute(query, achievement)
            
            conn.commit()
            logger.info(f"{len(achievements)} başarım veritabanına eklendi.")
        else:
            logger.info(f"Veritabanında zaten {count} başarım var, yeni başarım eklemiyorum.")
    except Exception as e:
        logger.error(f"Başarımlar eklenirken hata: {str(e)}")
        conn.rollback() if hasattr(conn, 'rollback') else None
    finally:
        conn.close()

def check_user_achievements(conn, user_id):
    """Check if user earned any new achievements based on contribution count"""
    cur = conn.cursor()
    
    # Veritabanı tipini kontrol et
    is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
    param_placeholder = '%s' if is_postgres else '?'
    
    try:
        # Get user's current contribution count
        query = f"SELECT contribution_count FROM users WHERE id = {param_placeholder}"
        cur.execute(query, (user_id,))
        result = cur.fetchone()
        
        if not result:
            return
            
        # PostgreSQL için farklı sonuç biçimi
        if is_postgres and isinstance(result, dict):
            contribution_count = result['contribution_count']
        else:
            contribution_count = result[0]
        
        # Get all achievements that the user qualifies for but hasn't earned yet
        query = f"""
            SELECT a.id 
            FROM achievements a 
            LEFT JOIN user_achievements ua ON a.id = ua.achievement_id AND ua.user_id = {param_placeholder} 
            WHERE ua.user_id IS NULL AND a.requirement_count <= {param_placeholder}
        """
        cur.execute(query, (user_id, contribution_count))
        
        new_achievements = cur.fetchall()
        
        # Award new achievements to the user
        for achievement in new_achievements:
            # PostgreSQL için farklı sonuç biçimi
            if is_postgres and isinstance(achievement, dict):
                achievement_id = achievement['id']
            else:
                achievement_id = achievement[0]
                
            insert_query = f"""
                INSERT INTO user_achievements (user_id, achievement_id)
                VALUES ({param_placeholder}, {param_placeholder})
            """
            cur.execute(insert_query, (user_id, achievement_id))
    except Exception as e:
        logger.error(f"Başarımlar kontrol edilirken hata: {str(e)}")
        # Bu fonksiyon başka bir transaction içinde çağrılabilir, bu yüzden burada commit/rollback yapmıyoruz
    
    # No need to commit here as it will be done by the caller

def get_top_contributors(limit=10):
    """Get top contributors based on the number of words they've added"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Veritabanı tipini kontrol et
    is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
    param_placeholder = '%s' if is_postgres else '?'
    
    try:
        logger.info("Popüler katılımcılar alınıyor")
        
        # Kullanıcıların katkı sayısını hesaplayan sorgu
        # words tablosundaki suggested_by sütununu kullanarak
        query = f"""
            SELECT u.id, u.username, COUNT(w.id) as contribution_count
            FROM users u
            LEFT JOIN words w ON u.id = w.suggested_by AND w.is_approved = 1
            GROUP BY u.id, u.username
            ORDER BY contribution_count DESC
            LIMIT {param_placeholder}
        """
        
        cur.execute(query, (limit,))
        
        results = cur.fetchall()
        
        # PostgreSQL için dict dönüşümü farklı
        if is_postgres:
            contributors = []
            for result in results:
                if isinstance(result, dict):
                    contributors.append(result)
                else:
                    contributors.append({
                        'id': result[0],
                        'username': result[1],
                        'contribution_count': result[2] if result[2] is not None else 0
                    })
            return contributors
        else:
            # SQLite için çevirme işlemi
            return [{'id': r[0], 'username': r[1], 'contribution_count': r[2] if r[2] is not None else 0} for r in results]
    except Exception as e:
        logger.error(f"Katkıda bulunanlar alınırken hata: {e}")
        return []
    finally:
        conn.close()

def register_user(username, email, password_hash):
    """Register a new user"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Veritabanı tipini kontrol et
    is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
    param_placeholder = '%s' if is_postgres else '?'
    
    try:
        query = f"""
            INSERT INTO users (username, email, password_hash)
            VALUES ({param_placeholder}, {param_placeholder}, {param_placeholder})
            RETURNING id
        """
        
        cur.execute(query, (username, email, password_hash))
        
        conn.commit()
        
        # PostgreSQL ve SQLite'da ID alma yöntemi farklı
        if is_postgres:
            # PostgreSQL için güvenli ID alma
            try:
                cur.execute("SELECT lastval()")
                user_id = cur.fetchone()[0]
            except Exception as e:
                logger.error(f"PostgreSQL ID alma hatası: {e}")
                # Alternatif olarak ID'yi doğrudan sorgula
                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                user_id = cur.fetchone()[0]
        else:
            # SQLite için
            user_id = cur.lastrowid
            
        return user_id
    except Exception as e:
        # Hata ayıklama için log kaydı
        logger.error(f"Error registering user: {str(e)}")
        conn.rollback() if hasattr(conn, 'rollback') else None
        # Username or email already exists
        conn.close()
        if "username" in str(e).lower():
            return "username_exists"
        elif "email" in str(e).lower():
            return "email_exists"
        return None
    except Exception as e:
        print(f"Error registering user: {e}")
        conn.close()
        return None

def get_user_by_username(username):
    """Get user by username"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    result = cur.fetchone()
    
    conn.close()
    return dict(result) if result else None

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    result = cur.fetchone()
    
    conn.close()
    return dict(result) if result else None

def get_user_achievements(user_id):
    """Get achievements earned by a user"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT a.id, a.name, a.description, a.icon, ua.earned_at
        FROM achievements a
        JOIN user_achievements ua ON a.id = ua.achievement_id
        WHERE ua.user_id = ?
        ORDER BY ua.earned_at
    """, (user_id,))
    
    results = cur.fetchall()
    conn.close()
    
    return [dict(result) for result in results]

def get_user_words(user_id, limit=20):
    """Get words suggested by a user"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT word, meaning, created_at
        FROM words
        WHERE suggested_by = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_id, limit))
    
    results = cur.fetchall()
    conn.close()
    
    return [dict(result) for result in results]

def get_pending_suggestions(limit=50):
    """Get pending word suggestions for admin review"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT s.*, u.username as suggested_by_username
        FROM suggestions s
        LEFT JOIN users u ON s.suggested_by = u.id
        WHERE s.status = 'pending'
        ORDER BY s.created_at ASC
        LIMIT ?
    """, (limit,))
    
    results = cur.fetchall()
    conn.close()
    
    # Convert row objects to dictionaries and ensure created_at is a datetime object
    suggestions = []
    for result in results:
        suggestion_dict = dict(result)
        if isinstance(suggestion_dict['created_at'], str):
            try:
                suggestion_dict['created_at'] = datetime.strptime(suggestion_dict['created_at'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # If parsing fails, just keep the string
                pass
        suggestions.append(suggestion_dict)
    
    return suggestions

def request_edit(word_id, new_meaning, reason, user_id):
    """Request an edit to a word's meaning"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Veritabanı tipini kontrol et
    is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
    param_placeholder = '%s' if is_postgres else '?'
    
    try:
        # Dinamik sorgu oluştur
        query = f"""
            INSERT INTO edit_requests 
                (word_id, new_meaning, reason, requested_by, status) 
            VALUES ({param_placeholder}, {param_placeholder}, {param_placeholder}, {param_placeholder}, 'pending')
        """
        
        if is_postgres:
            query += " RETURNING id"
            cur.execute(query, (word_id, new_meaning, reason, user_id))
            request_id = cur.fetchone()[0]
        else:
            cur.execute(query, (word_id, new_meaning, reason, user_id))
            request_id = cur.lastrowid
        
        conn.commit()
        return True, request_id
    except Exception as e:
        logger.error(f"Error requesting edit: {e}")
        conn.rollback() if hasattr(conn, 'rollback') else None
        return False, str(e)
    finally:
        conn.close()

def get_pending_edit_requests(limit=50):
    """Get pending edit requests for admin review"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT er.*, w.word, w.meaning as current_meaning, u.username as requested_by_username
        FROM edit_requests er
        JOIN words w ON er.word_id = w.id
        LEFT JOIN users u ON er.requested_by = u.id
        WHERE er.status = 'pending'
        ORDER BY er.created_at ASC
        LIMIT ?
    """, (limit,))
    
    results = cur.fetchall()
    conn.close()
    
    # Convert row objects to dictionaries and ensure created_at is a datetime object
    edit_requests = []
    for result in results:
        request_dict = dict(result)
        if isinstance(request_dict['created_at'], str):
            try:
                request_dict['created_at'] = datetime.strptime(request_dict['created_at'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # If parsing fails, just keep the string
                pass
        edit_requests.append(request_dict)
    
    return edit_requests

def approve_edit_request(request_id, admin_id):
    """Approve an edit request and update the word's meaning"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get the edit request
        cur.execute("SELECT * FROM edit_requests WHERE id = ?", (request_id,))
        request = cur.fetchone()
        
        if not request:
            conn.close()
            return False, "Değişiklik talebi bulunamadı"
        
        # Update the word's meaning
        cur.execute("""
            UPDATE words 
            SET meaning = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (request['new_meaning'], request['word_id']))
        
        # Update request status
        cur.execute("""
            UPDATE edit_requests 
            SET status = 'approved' 
            WHERE id = ?
        """, (request_id,))
        
        conn.commit()
        conn.close()
        return True, "Değişiklik talebi onaylandı"
    except Exception as e:
        print(f"Error approving edit request: {e}")
        conn.close()
        return False, str(e)

def reject_edit_request(request_id, admin_id, admin_notes=None):
    """Reject an edit request"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Update request status
        cur.execute("""
            UPDATE edit_requests 
            SET status = 'rejected', admin_notes = ? 
            WHERE id = ?
        """, (admin_notes, request_id))
        
        conn.commit()
        conn.close()
        return True, "Değişiklik talebi reddedildi"
    except Exception as e:
        logger.error(f"Edit isteğini reddetme hatası: {e}")
        conn.close()
        return False, str(e)

def vote_word(word_id, user_id, vote_type):
    """Vote on a word (up or down)"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        if vote_type == 'up':
            cur.execute("UPDATE words SET votes_up = votes_up + 1 WHERE id = ?", (word_id,))
        elif vote_type == 'down':
            cur.execute("UPDATE words SET votes_down = votes_down + 1 WHERE id = ?", (word_id,))
        else:
            conn.close()
            return False, "Geçersiz oy tipi"
        
        conn.commit()
        conn.close()
        return True, "Oy başarıyla kaydedildi"
    except Exception as e:
        print(f"Error voting: {e}")
        conn.close()
        return False, str(e)

def is_admin(user_id):
    """Check if a user is an admin"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT is_admin FROM users WHERE id = ?", (user_id,))
    result = cur.fetchone()
    
    conn.close()
    return result and result['is_admin'] == 1


def get_total_words_count():
    """Get the total count of approved words in the dictionary"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM words WHERE is_approved = 1")
    result = cur.fetchone()
    
    conn.close()
    return result['count'] if result else 0


def get_total_users_count():
    """Get the total count of registered users"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM users")
    result = cur.fetchone()
    
    conn.close()
    return result['count'] if result else 0


def get_words_added_today():
    """Get the count of words added today"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT COUNT(*) as count 
        FROM words 
        WHERE is_approved = 1 
        AND date(approved_at) = date('now')
    """)
    result = cur.fetchone()
    
    conn.close()
    return result['count'] if result else 0


def get_words_added_this_month():
    """Get the count of words added this month"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT COUNT(*) as count 
        FROM words 
        WHERE is_approved = 1 
        AND strftime('%Y-%m', approved_at) = strftime('%Y-%m', 'now')
    """)
    result = cur.fetchone()
    
    conn.close()
    return result['count'] if result else 0


def get_pending_counts():
    """Get counts of pending suggestions and edit requests"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as suggestion_count FROM suggestions WHERE status = 'pending'")
    pending_suggestions = cur.fetchone()['suggestion_count']
    
    cur.execute("SELECT COUNT(*) as edit_count FROM edit_requests WHERE status = 'pending'")
    pending_edits = cur.fetchone()['edit_count']
    
    conn.close()
    return {
        'pending_suggestions': pending_suggestions,
        'pending_edits': pending_edits
    }
