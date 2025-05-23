import os
import sqlite3
import logging

# Logging ayarlaması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('db_config')

def get_db_connection():
    """
    SQLite veritabanı bağlantısı oluşturur.
    """
    logger.info("SQLite veritabanı kullanılıyor")
    return get_sqlite_connection()

def get_sqlite_connection():
    """SQLite veritabanı bağlantısı oluşturur"""
    # Önce mevcut dizini kontrol et
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'zgen_translator.db')
    
    # Mevcut dizine yazma izni kontrolü
    if os.access(current_dir, os.W_OK):
        logger.info(f"Mevcut dizine yazma izni var: {current_dir}")
    else:
        # /tmp dizinini dene
        db_path = "/tmp/zgen_translator.db"
        logger.info(f"Mevcut dizine yazma izni yok, /tmp kullanılıyor: {db_path}")
    
    logger.info(f"SQLite veritabanı yolu: {db_path}")
    
    try:
        # Veritabanı dosyasının bulunduğu dizini oluştur (eğer yoksa)
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        # Veritabanına bağlan
        conn = sqlite3.connect(db_path, timeout=30.0)  # Timeout süresini artır
        conn.row_factory = sqlite3.Row  # Dict benzeri sonuçlar için
        
        # Bağlantıyı test et
        cursor = conn.cursor()
        cursor.execute('PRAGMA journal_mode=WAL')  # Daha iyi eşzamanlılık için
        cursor.execute('PRAGMA busy_timeout=30000')  # 30 saniye bekleme süresi
        cursor.execute('SELECT 1')
        cursor.fetchone()
        cursor.close()
        
        logger.info("SQLite bağlantısı başarılı")
        return conn
    except Exception as e:
        logger.error(f"SQLite bağlantı hatası: {e}")
        # Hata durumunda bellekte çalışan bir veritabanı kullan
        logger.info("Bellek içi SQLite veritabanına geçiliyor...")
        try:
            memory_conn = sqlite3.connect(':memory:')
            memory_conn.row_factory = sqlite3.Row
            # Gerekli tabloları oluştur
            cursor = memory_conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    contribution_count INTEGER DEFAULT 0,
                    is_admin INTEGER DEFAULT 0
                )
            ''')
            memory_conn.commit()
            cursor.close()
            return memory_conn
        except Exception as mem_err:
            logger.error(f"Bellek içi veritabanı başlatılamadı: {mem_err}")
            raise
