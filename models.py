import os
import logging
import sqlite3
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
    if hasattr(conn, 'cursor_factory'):  # PostgreSQL bağlantısı
        return '%s'
    return '?'  # SQLite bağlantısı

# get_db_connection fonksiyonu artık db_config.py'de

def init_db():
    """Initialize the database with tables if they don't exist"""
    import logging
    logger = logging.getLogger('models')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        logger.info("Veritabanı tablolarını oluşturma başlatılıyor...")
        
        # PostgreSQL için farklı PRIMARY KEY sözdizimi gerekebilir
        is_postgres = hasattr(conn, 'cursor_factory')
        
        if is_postgres:
            # PostgreSQL için tablo oluşturma
            # PostgreSQL'de AUTOINCREMENT yerine SERIAL kullanılır
            logger.info("PostgreSQL için tablolar oluşturuluyor...")
            
            # Create words table
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
            
            # PostgreSQL için parametre yerleştirici %s kullan
            for word, meaning in initial_words.items():
                current_time = datetime.now()
                try:
                    cur.execute(
                        "INSERT INTO words (word, meaning, is_approved, approved_at) VALUES (%s, %s, 1, %s)",
                        (word, meaning, current_time)
                    )
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
    
    # Only get approved words
    cur.execute("""
        SELECT w.*, u.username as suggested_by_username
        FROM words w
        LEFT JOIN users u ON w.suggested_by = u.id
        WHERE w.word = ? COLLATE NOCASE AND w.is_approved = 1
        ORDER BY w.votes_up DESC
    """, (word,))
    
    results = cur.fetchall()
    
    conn.close()
    return [dict(result) for result in results] if results else None

def add_word(word, meaning, suggested_by=None):
    """Add a new word to the database as a suggestion (pending approval)"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Instead of directly adding to words table, add to suggestions
        cur.execute(
            "INSERT INTO suggestions (word, meaning, suggested_by, status) VALUES (?, ?, ?, ?)",
            (word.lower(), meaning, suggested_by, 'pending')
        )
        suggestion_id = cur.lastrowid
        
        conn.commit()
        conn.close()
        return suggestion_id
    except Exception as e:
        print(f"Error adding suggestion: {e}")
        conn.close()
        return None

def approve_word(suggestion_id, admin_id):
    """Approve a word suggestion and add it to the words table"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get the suggestion
        cur.execute("SELECT * FROM suggestions WHERE id = ?", (suggestion_id,))
        suggestion = cur.fetchone()
        
        if not suggestion:
            conn.close()
            return False, "Öneri bulunamadı"
        
        # Add the word to the words table
        cur.execute(
            """INSERT INTO words 
                (word, meaning, suggested_by, is_approved, approved_by, approved_at) 
                VALUES (?, ?, ?, 1, ?, CURRENT_TIMESTAMP)""",
            (suggestion['word'], suggestion['meaning'], suggestion['suggested_by'], admin_id)
        )
        word_id = cur.lastrowid
        
        # Update suggestion status
        cur.execute(
            "UPDATE suggestions SET status = 'approved' WHERE id = ?",
            (suggestion_id,)
        )
        
        # Update user's contribution count if user exists
        if suggestion['suggested_by']:
            cur.execute(
                "UPDATE users SET contribution_count = contribution_count + 1 WHERE id = ?",
                (suggestion['suggested_by'],)
            )
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
    
    try:
        # Update suggestion status
        cur.execute(
            "UPDATE suggestions SET status = 'rejected', admin_notes = ? WHERE id = ?",
            (admin_notes, suggestion_id)
        )
        
        conn.commit()
        conn.close()
        return True, "Öneri reddedildi"
    except Exception as e:
        print(f"Error rejecting word: {e}")
        conn.close()
        return False, str(e)

def add_suggestion(word, meaning, suggested_by=None):
    """Add a new word suggestion to the database"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            "INSERT INTO suggestions (word, meaning, suggested_by) VALUES (?, ?, ?)",
            (word.lower(), meaning, suggested_by)
        )
        conn.commit()
        success = True
    except Exception as e:
        print(f"Error adding suggestion: {e}")
        success = False
    
    conn.close()
    return success

def get_popular_words(limit=10):
    """Get a list of popular words from the database"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Oncelikle is_approved=1 olan kelimeleri dene
    cur.execute("""
        SELECT w.id, w.word, w.meaning, w.created_at, u.username as added_by, w.votes_up
        FROM words w 
        LEFT JOIN users u ON w.suggested_by = u.id 
        WHERE w.is_approved = 1
        ORDER BY w.votes_up DESC, w.created_at DESC LIMIT ?
    """, (limit,))
    results = cur.fetchall()
    
    # Eğer onaylı kelime yoksa, varsayılan sözlükteki kelimeleri göster
    if not results:
        cur.execute("""
            SELECT w.id, w.word, w.meaning, w.created_at, u.username as added_by, w.votes_up
            FROM words w 
            LEFT JOIN users u ON w.suggested_by = u.id 
            ORDER BY w.votes_up DESC, w.created_at DESC LIMIT ?
        """, (limit,))
        results = cur.fetchall()
    
    conn.close()
    return [dict(result) for result in results]

def seed_initial_achievements():
    """Seed the database with initial achievements"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if achievements already exist
    cur.execute("SELECT COUNT(*) FROM achievements")
    count = cur.fetchone()[0]
    
    if count == 0:
        print("Başarımları veritabanına ekliyorum...")
        achievements = [
            ("Yeni Çevirmen", "İlk kelimeni ekledin!", "📝", 1),
            ("Kelime Ustası", "10 kelime ekledin", "🔤", 10),
            ("Z Kuşağı Çevirmeni", "25 kelime ekledin", "💬", 25),
            ("Dil Dehası", "50 kelime ekledin", "🏆", 50),
            ("Z-Sözlük Oluşturucu", "100 kelime ekledin", "👑", 100)
        ]
        
        cur.executemany("""
            INSERT INTO achievements (name, description, icon, requirement_count)
            VALUES (?, ?, ?, ?)
        """, achievements)
        
        conn.commit()
        print(f"{len(achievements)} başarım veritabanına eklendi.")
    else:
        print(f"Veritabanında zaten {count} başarım var, yeni başarım eklemiyorum.")
    
    conn.close()

def check_user_achievements(conn, user_id):
    """Check if user earned any new achievements based on contribution count"""
    cur = conn.cursor()
    
    # Get user's current contribution count
    cur.execute("SELECT contribution_count FROM users WHERE id = ?", (user_id,))
    result = cur.fetchone()
    
    if not result:
        return
        
    contribution_count = result[0]
    
    # Get all achievements that the user qualifies for but hasn't earned yet
    cur.execute("""
        SELECT a.id 
        FROM achievements a 
        LEFT JOIN user_achievements ua ON a.id = ua.achievement_id AND ua.user_id = ? 
        WHERE ua.user_id IS NULL AND a.requirement_count <= ?
    """, (user_id, contribution_count))
    
    new_achievements = cur.fetchall()
    
    # Award new achievements to the user
    for achievement in new_achievements:
        achievement_id = achievement[0]
        cur.execute("""
            INSERT INTO user_achievements (user_id, achievement_id)
            VALUES (?, ?)
        """, (user_id, achievement_id))
    
    # No need to commit here as it will be done by the caller

def get_top_contributors(limit=10):
    """Get top contributors based on contribution count"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, username, contribution_count 
        FROM users 
        ORDER BY contribution_count DESC LIMIT ?
    """, (limit,))
    
    results = cur.fetchall()
    conn.close()
    
    return [dict(result) for result in results]

def register_user(username, email, password_hash):
    """Register a new user"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        """, (username, email, password_hash))
        
        conn.commit()
        user_id = cur.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError as e:
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
    
    try:
        cur.execute("""
            INSERT INTO edit_requests 
                (word_id, new_meaning, reason, requested_by, status) 
            VALUES (?, ?, ?, ?, 'pending')
        """, (word_id, new_meaning, reason, user_id))
        
        request_id = cur.lastrowid
        conn.commit()
        conn.close()
        return True, request_id
    except Exception as e:
        print(f"Error requesting edit: {e}")
        conn.close()
        return False, str(e)

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
