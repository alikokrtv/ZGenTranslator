import os
import sqlite3
import logging
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    RealDictCursor = None

# Logging ayarlaması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('db_config')

def get_db_connection():
    """
    Veritabanı bağlantısı oluşturur.
    Railway PostgreSQL varsa onu kullanır, yoksa SQLite'a döner.
    """
    # Railway PostgreSQL ortam değişkenini kontrol et
    if 'DATABASE_URL' in os.environ or 'PGDATABASE' in os.environ:
        logger.info("PostgreSQL veritabanı kullanılıyor (Railway)")
        return get_postgres_connection()
    else:
        logger.info("SQLite veritabanı kullanılıyor (Railway PostgreSQL bulunamadı)")
        return get_sqlite_connection()
        
def get_postgres_connection():
    """
    Railway PostgreSQL veritabanı bağlantısı oluşturur
    """
    try:
        # Railway PostgreSQL bağlantı bilgilerini ortam değişkenlerinden al
        if 'DATABASE_URL' in os.environ:
            # DATABASE_URL formatlı bağlantı kullan
            database_url = os.environ['DATABASE_URL']
            logger.info(f"DATABASE_URL kullanılıyor: {database_url[:20]}...")
            conn = psycopg2.connect(database_url)
        else:
            # Ayrı ortam değişkenlerini kullan
            db_params = {
                'dbname': os.environ.get('PGDATABASE', 'postgres'),
                'user': os.environ.get('PGUSER', 'postgres'),
                'password': os.environ.get('PGPASSWORD', ''),
                'host': os.environ.get('PGHOST', 'localhost'),
                'port': os.environ.get('PGPORT', '5432')
            }
            logger.info(f"PostgreSQL bağlantı parametreleri: {db_params['host']}:{db_params['port']}, DB: {db_params['dbname']}")
            conn = psycopg2.connect(**db_params)
        
        # RealDictCursor kullanarak, sonuçları sözlük olarak al
        conn.cursor_factory = RealDictCursor
        
        # Bağlantıyı test et
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        cursor.close()
        
        logger.info("PostgreSQL bağlantısı başarılı")
        return conn
    except Exception as e:
        logger.error(f"PostgreSQL bağlantı hatası: {str(e)}", exc_info=True)
        logger.warning("PostgreSQL bağlantısı başarısız, SQLite'a geçiliyor...")
        return get_sqlite_connection()

def get_sqlite_connection():
    """SQLite veritabanı bağlantısı oluşturur"""
    # Önce mevcut dizini kontrol et
    current_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(current_dir, 'zgen_translator.db'),  # Current directory - Öncelikli
        os.path.join(current_dir, 'instance', 'zgen_translator.db'),  # Flask default instance path
        '/tmp/zgen_translator.db',  # System temp directory
        '/app/zgen_translator.db',  # Common container path
    ]
    
    logger.info(f"Kontrol edilen veritabanı yolları: {possible_paths}")
    
    # Yazılabilir bir dizin bul
    db_path = None
    for path in possible_paths:
        try:
            dir_path = os.path.dirname(os.path.abspath(path))
            os.makedirs(dir_path, exist_ok=True)
            if os.access(dir_path, os.W_OK):
                db_path = path
                logger.info(f"Veritabanı için yazılabilir dizin bulundu: {dir_path}")
                break
        except Exception as e:
            logger.warning(f"{path} dizini kullanılamıyor: {str(e)}")
    
    if db_path is None:
        logger.warning("Yazılabilir bir dizin bulunamadı, bellek içi veritabanı kullanılacak")
        return create_in_memory_db()
    
    logger.info(f"Veritabanı dosya yolu: {db_path}")
    
    try:
        # Veritabanı dosyasının bulunduğu dizini oluştur (eğer yoksa)
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        logger.info(f"SQLite veritabanına bağlanılıyor: {db_path}")
        logger.info(f"Mevcut izinler: {os.stat(os.path.dirname(db_path))}")
        
        # Veritabanına bağlan
        conn = sqlite3.connect(db_path, timeout=30.0)  # Timeout süresini artır
        conn.row_factory = sqlite3.Row  # Dict benzeri sonuçlar için
        
        # Bağlantıyı test et
        cursor = conn.cursor()
        cursor.execute('PRAGMA journal_mode=WAL')  # Daha iyi eşzamanlılık için
        cursor.execute('PRAGMA busy_timeout=30000')  # 30 saniye bekleme süresi
        cursor.execute('PRAGMA foreign_keys=ON')  # Foreign key desteğini etkinleştir
        cursor.execute('SELECT 1')
        cursor.fetchone()
        cursor.close()
        
        logger.info(f"SQLite bağlantısı başarılı: {db_path}")
        return conn
    except Exception as e:
        logger.error(f"SQLite bağlantı hatası: {str(e)}", exc_info=True)
        # Hata durumunda bellekte çalışan bir veritabanı kullan
        logger.warning("Bellek içi SQLite veritabanına geçiliyor...")
        return create_in_memory_db()

def create_in_memory_db():
    """Bellek içi SQLite veritabanı oluşturur"""
    try:
        logger.info("Bellek içi SQLite veritabanı oluşturuluyor...")
        memory_conn = sqlite3.connect(':memory:', check_same_thread=False)
        memory_conn.row_factory = sqlite3.Row
        
        # Gerekli tabloları oluştur
        cursor = memory_conn.cursor()
        
        # Users tablosu
        cursor.execute('''
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
        
        # Words tablosu
        cursor.execute('''
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
                FOREIGN KEY (suggested_by) REFERENCES users(id) ON DELETE SET NULL
            )
        ''')
        
        memory_conn.commit()
        cursor.close()
        
        logger.info("Bellek içi veritabanı başarıyla oluşturuldu")
        return memory_conn
    except Exception as e:
        logger.critical(f"Bellek içi veritabanı oluşturulamadı: {str(e)}", exc_info=True)
        raise
