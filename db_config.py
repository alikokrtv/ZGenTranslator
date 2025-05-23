import os
import sqlite3
import psycopg2
import logging
from psycopg2.extras import DictCursor

# Logging ayarlaması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('db_config')

def get_db_connection():
    """
    Veritabanı bağlantısı oluşturur.
    Railway PostgreSQL veya yerel SQLite kullanabilir.
    """
    # Railway PostgreSQL bağlantı URL'si
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url and database_url.startswith('postgres'):
        # PostgreSQL bağlantısı
        try:
            logger.info(f"PostgreSQL veritabanına bağlanılıyor...")
            conn = psycopg2.connect(database_url)
            conn.cursor_factory = DictCursor  # Dict benzeri sonuçlar için
            logger.info("PostgreSQL bağlantısı başarılı")
            return conn
        except Exception as e:
            logger.error(f"PostgreSQL bağlantı hatası: {e}")
            logger.info("SQLite'a geri dönülüyor...")
            # Hata durumunda SQLite'a geri dön
            return get_sqlite_connection()
    else:
        # SQLite bağlantısı
        logger.info("SQLite veritabanı kullanılıyor")
        return get_sqlite_connection()

def get_sqlite_connection():
    """SQLite veritabanı bağlantısı oluşturur"""
    db_path = os.path.join(os.path.dirname(__file__), 'zgen_translator.db')
    logger.info(f"SQLite yolu: {db_path}")
    
    if not os.path.exists(db_path):
        logger.warning(f"SQLite veritabanı dosyası bulunamadı: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Dict benzeri sonuçlar için
    return conn
