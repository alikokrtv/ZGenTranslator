import os
import sqlite3
import logging

try:
    import pymysql
    pymysql.install_as_MySQLdb()
    HAVE_MYSQL = True
except ImportError:
    HAVE_MYSQL = False

try:
    import psycopg2
    from psycopg2.extras import DictCursor
    HAVE_POSTGRES = True
except ImportError:
    HAVE_POSTGRES = False

# Logging ayarlaması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('db_config')

def get_db_connection():
    """
    Veritabanı bağlantısı oluşturur.
    MySQL, PostgreSQL veya SQLite kullanır.
    """
    # MySQL bağlantı bilgileri
    mysql_url = os.environ.get('MYSQL_URL')
    mysql_host = os.environ.get('MYSQLHOST')
    mysql_user = os.environ.get('MYSQLUSER')
    mysql_password = os.environ.get('MYSQLPASSWORD')
    mysql_database = os.environ.get('MYSQLDATABASE')
    mysql_port = os.environ.get('MYSQLPORT')
    
    # Railway PostgreSQL bağlantı URL'si
    database_url = os.environ.get('DATABASE_URL')
    
    # Öncelikle MySQL bağlantısını dene
    if HAVE_MYSQL and mysql_host and mysql_user and mysql_password and mysql_database:
        try:
            logger.info("MySQL veritabanına bağlanılıyor...")
            conn = pymysql.connect(
                host=mysql_host,
                user=mysql_user,
                password=mysql_password,
                database=mysql_database,
                port=int(mysql_port) if mysql_port else 3306,
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info("MySQL bağlantısı başarılı")
            return conn
        except Exception as e:
            logger.error(f"MySQL bağlantı hatası: {e}")
            logger.info("Diğer bağlantı yöntemlerine geçiliyor...")
    
    # MySQL bağlantısı olmazsa PostgreSQL'i dene
    if database_url and HAVE_POSTGRES:
        try:
            logger.info("PostgreSQL veritabanına bağlanılıyor...")
            conn = psycopg2.connect(database_url)
            conn.cursor_factory = DictCursor  # Dict benzeri sonuçlar için
            logger.info("PostgreSQL bağlantısı başarılı")
            return conn
        except Exception as e:
            logger.error(f"PostgreSQL bağlantı hatası: {e}")
            logger.info("SQLite'a geri dönülüyor...")
    else:
        if not (mysql_host or database_url):
            logger.warning("Veritabanı bağlantı bilgileri bulunamadı, SQLite kullanılıyor")
        elif not (HAVE_MYSQL or HAVE_POSTGRES):
            logger.warning("Veritabanı kütüphaneleri yüklenemedi, SQLite kullanılıyor")
    
    # SQLite bağlantısı oluştur (son çare)
    return get_sqlite_connection()

def get_sqlite_connection():
    """SQLite veritabanı bağlantısı oluşturur"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zgen_translator.db')
    logger.info(f"SQLite veritabanı yolu: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Dict benzeri sonuçlar için
    return conn
