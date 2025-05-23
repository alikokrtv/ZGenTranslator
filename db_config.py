import os
import psycopg2
import logging
from psycopg2.extras import DictCursor

# Logging ayarlaması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('db_config')

def get_db_connection():
    """
    PostgreSQL veritabanı bağlantısı oluşturur.
    Railway için optimize edilmiştir.
    """
    # Railway PostgreSQL bağlantı URL'si
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        logger.error("DATABASE_URL çevre değişkeni bulunamadı")
        raise Exception("PostgreSQL bağlantısı için DATABASE_URL çevre değişkeni gerekli")
    
    try:
        logger.info("PostgreSQL veritabanına bağlanılıyor...")
        conn = psycopg2.connect(database_url)
        conn.cursor_factory = DictCursor  # Dict benzeri sonuçlar için
        logger.info("PostgreSQL bağlantısı başarılı")
        return conn
    except Exception as e:
        logger.error(f"PostgreSQL bağlantı hatası: {e}")
        raise Exception(f"Veritabanı bağlantı hatası: {e}")
