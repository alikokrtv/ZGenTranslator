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
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zgen_translator.db')
    logger.info(f"SQLite veritabanı yolu: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Dict benzeri sonuçlar için
    return conn
