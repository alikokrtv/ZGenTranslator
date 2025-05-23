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
    # Railway için uygun bir yol seç
    # /tmp klasörü, bulut platformlarında genellikle yazma izni olan bir dizindir
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        # Railway'deyiz, /tmp dizinini kullan
        db_path = "/tmp/zgen_translator.db"
    else:
        # Yerel ortamdayız, normal yolu kullan
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zgen_translator.db')
    
    logger.info(f"SQLite veritabanı yolu: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Dict benzeri sonuçlar için
        
        # Bağlantıyı test et
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        cursor.close()
        
        logger.info("SQLite bağlantısı başarılı")
        return conn
    except Exception as e:
        logger.error(f"SQLite bağlantı hatası: {e}")
        # Hata mesajını göster ama devam et
        # Bellek içi veritabanı kullan
        logger.info("Bellek içi SQLite veritabanına geçiliyor...")
        memory_conn = sqlite3.connect(':memory:')
        memory_conn.row_factory = sqlite3.Row
        return memory_conn
