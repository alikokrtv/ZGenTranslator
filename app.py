import os
import json
import hashlib
import logging
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, abort, request, Response
from email_system import init_mail, new_word_suggestion_notification, edit_request_notification, user_registration_notification
from db_config import get_db_connection
from models import (init_db, get_word, add_word, add_suggestion, get_popular_words, 
                  register_user, get_user_by_username, get_user_by_id, get_user_achievements, 
                  get_user_words, get_top_contributors, is_admin, get_pending_suggestions,
                  approve_word, reject_word, request_edit, get_pending_edit_requests,
                  approve_edit_request, reject_edit_request, vote_word, get_total_words_count,
                  get_total_users_count, get_words_added_today, get_words_added_this_month,
                  get_pending_counts)

# Logging ayarı
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('app')

# Create Flask app
app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = os.environ.get("SESSION_SECRET", "z-kusagi-translator-secret")

# Configure app to ensure proper static file serving
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching during development

# E-posta sistemini başlat
mail = init_mail(app)

# Veritabanı tablolarını oluştur
try:
    logger.info("Veritabanı tablolarını oluşturmaya başlıyor...")
    init_db()
    logger.info("Veritabanı tabloları başarıyla oluşturuldu")
except Exception as e:
    logger.error(f"Veritabanı tabloları oluşturulurken hata: {e}")
    print(f"Veritabanı hata: {e}")


# HTTP'den HTTPS'ye yönlendirme middleware'i - Cloudflare kullanıldığı için devre dışı bırakıldı
class HTTPSRedirectMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Cloudflare zaten HTTP'den HTTPS'ye yönlendirme işlemini yapıyor
        # Bu nedenle kendi yönlendirme kodumuz devre dışı bırakıldı
        # Sadece uygulamayı normal şekilde çalıştır
        return self.app(environ, start_response)

# Middleware'i sadece prodüksiyonda etkinleştir
if os.environ.get('FLASK_ENV', 'development') == 'production':
    app.wsgi_app = HTTPSRedirectMiddleware(app.wsgi_app)

# Initialize database with error handling
try:
    logger.info("Veritabanı başlatılıyor...")
    logger.info(f"Çalışma dizini: {os.getcwd()}")
    logger.info(f"Mevcut dosyalar: {os.listdir('.')}")
    init_db()
    logger.info("Veritabanı başlatma tamamlandı")
except Exception as e:
    import traceback
    logger.error(f"Veritabanı başlatma hatası: {str(e)}")
    logger.error(f"Hata detayı: {traceback.format_exc()}")
    logger.error("Uygulama devam ediyor ancak veritabanı işlevselliği sınırlı olabilir.")

# Add a test route to check basic functionality
@app.route('/test')
def test():
    """Test endpoint to check basic functionality"""
    try:
        # Test database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # Test template rendering
        template_test = render_template('test.html')
        
        return jsonify({
            'status': 'success',
            'database': 'connected',
            'templates': 'working',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        import traceback
        return jsonify({
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Add a simple health check endpoint
@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    try:
        # Test database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'database': 'connection failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Admin authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        
        if not is_admin(session['user_id']):
            flash('Bu sayfaya erişim yetkiniz yok.', 'error')
            return redirect(url_for('index'))
            
        return f(*args, **kwargs)
    return decorated_function

# Route for home page
@app.route('/')
def index():
    try:
        user = None
        is_user_admin = False
        if 'user_id' in session:
            try:
                user = get_user_by_id(session['user_id'])
                is_user_admin = is_admin(session['user_id']) if user else False
            except Exception as e:
                logger.error(f"Kullanıcı bilgileri alınırken hata: {e}")
                session.clear()  # Geçersiz oturumu temizle
        
        try:
            top_contributors = get_top_contributors(5)
        except Exception as e:
            logger.error(f"En iyi katkıda bulunanlar alınırken hata: {e}")
            top_contributors = []
        
        try:
            popular_words = get_popular_words(10)
            logger.info(f"Popüler kelimeler: {popular_words}")
            # Popüler kelimelerin içeriğini görelim
            for word in popular_words:
                logger.info(f"Kelime: {word}")
        except Exception as e:
            logger.error(f"Popüler kelimeler alınırken hata: {e}")
            import traceback
            logger.error(f"Hata detayı: {traceback.format_exc()}")
            popular_words = []
            
        return render_template('index.html', user=user, top_contributors=top_contributors, popular_words=popular_words, is_admin=is_user_admin)
    except Exception as e:
        logger.error(f"Ana sayfa yüklenirken beklenmeyen hata: {e}")
        return render_template('error.html', error_message="Üzgünüz, bir hata oluştu. Lütfen daha sonra tekrar deneyiniz."), 500

@app.route('/popular', methods=['GET'])
def popular_words():
    try:
        # Sadece 10 kelime getir
        words = get_popular_words(10)
        
        # Kullanıcı bilgilerini al
        user = None
        is_admin = False
        
        if 'user_id' in session:
            user = get_user_by_id(session['user_id'])
            if user:
                is_admin = user.get('is_admin', False)
        
        # Debug için konsola yazdır
        print(f"Toplam {len(words)} kelime bulundu.")
        for word in words:
            print(f"Kelime: {word.get('word')}, Upvotes: {word.get('upvotes')}")
        
        return render_template('popular.html', 
                            user=user, 
                            words=words,
                            is_admin=is_admin)
    except Exception as e:
        logger.error(f"Popüler kelimeler yüklenirken hata: {e}", exc_info=True)
        return render_template('error.html', 
                            error_message="Popüler kelimeler yüklenirken bir hata oluştu.",
                            user=None,
                            is_admin=False), 500

# User registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('profile'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not username or not email or not password:
            flash('Tüm alanları doldurmanız gerekiyor.', 'error')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Şifreler eşleşmiyor.', 'error')
            return render_template('register.html')
            
        if len(password) < 6:
            flash('Şifre en az 6 karakter olmalıdır.', 'error')
            return render_template('register.html')
            
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Register user
        result = register_user(username, email, password_hash)
        
        if result == 'username_exists':
            flash('Bu kullanıcı adı zaten kullanılıyor.', 'error')
            return render_template('register.html')
            
        if result == 'email_exists':
            flash('Bu e-posta adresi zaten kullanılıyor.', 'error')
            return render_template('register.html')
            
        if result:
            # Auto login after registration
            session['user_id'] = result
            # Başarılı kayıt için e-posta bildirimi gönder
            user_registration_notification(username, email)
            flash('Kayıt işlemi başarılı! Şimdi giriş yapabilirsiniz.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Kayıt sırasında bir hata oluştu. Lütfen tekrar deneyin.', 'error')
            
    return render_template('register.html')

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Log for debugging
    logger.info(f"Login route called with method: {request.method}")
    logger.info(f"Form data: {request.form if request.method == 'POST' else 'N/A'}")
    
    if 'user_id' in session:
        logger.info("User already logged in, redirecting to profile")
        return redirect(url_for('profile'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        logger.info(f"Login attempt for username: {username}")
        
        if not username or not password:
            logger.warning("Missing username or password")
            flash('Kullanıcı adı ve şifre gereklidir.', 'error')
            return render_template('login.html')
            
        # Get user
        user = get_user_by_username(username)
        
        if not user:
            logger.warning(f"User not found: {username}")
            flash('Kullanıcı adı veya şifre hatalı.', 'error')
            return render_template('login.html')
            
        # Check password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        logger.info(f"Password check for user {username}: {'success' if user['password_hash'] == password_hash else 'failed'}")
        
        if user['password_hash'] != password_hash:
            logger.warning(f"Password mismatch for user: {username}")
            flash('Kullanıcı adı veya şifre hatalı.', 'error')
            return render_template('login.html')
            
        # Login successful
        logger.info(f"Login successful for user: {username}")
        session['user_id'] = user['id']
        flash('Giriş başarılı! Hoş geldiniz.', 'success')
        
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('profile'))
        
    return render_template('login.html')

# Veritabanı parametre yer tutucusu fonksiyonu
def get_param_placeholder(conn):
    # PostgreSQL için %s, SQLite için ? kullan
    is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
    return '%s' if is_postgres else '?'

# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('index'))

# User profile
@app.route('/profile')
@login_required
def profile():
    user = get_user_by_id(session['user_id'])
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('login'))
        
    user_achievements = get_user_achievements(user['id'])
    user_words = get_user_words(user['id'])
    
    return render_template('profile.html', user=user, achievements=user_achievements, words=user_words)

# Leaderboard - En çok katkıda bulunanlar
@app.route('/leaderboard')
def leaderboard():
    top_contributors = get_top_contributors(20)
    return render_template('leaderboard.html', contributors=top_contributors)

# Legal pages
@app.route('/privacy')
def privacy_policy():
    return render_template('privacy.html')

@app.route('/terms')
def terms_of_service():
    return render_template('terms.html')

@app.route('/cookies')
def cookie_policy():
    return render_template('cookies.html')

# API endpoint to get translation
@app.route('/translate', methods=['POST'])
def translate():
    word = request.form.get('word', '').strip().lower()
    
    if not word:
        return jsonify({
            'success': False,
            'message': 'Lütfen bir kelime girin!'
        })
    
    # Get word meanings from database
    results = get_word(word)
    
    # Check if user is logged in for the edit request feature
    user_logged_in = 'user_id' in session
    user = None
    if user_logged_in:
        user = get_user_by_id(session['user_id'])
    
    if results:
        # Format results for the frontend
        formatted_results = []
        for result in results:
            contributor = None
            if result.get('suggested_by'):
                user_data = get_user_by_id(result['suggested_by'])
                if user_data:
                    contributor = user_data['username']
            
            formatted_results.append({
                'id': result['id'],
                'meaning': result['meaning'],
                'contributor': contributor,
                'votes_up': result['votes_up'],
                'votes_down': result['votes_down']
            })
        
        return jsonify({
            'success': True,
            'word': word,
            'meanings': formatted_results,
            'user_logged_in': user_logged_in
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Bu kelimeyi bilmiyorum 😢 Ama sen öğretebilirsin!',
            'user': user['username'] if user else None
        })

# API endpoint to suggest new word
@app.route('/suggest', methods=['POST'])
def suggest():
    word = request.form.get('word', '').lower().strip()
    meaning = request.form.get('meaning', '').strip()
    name = request.form.get('name', '').strip()
    
    if not word or not meaning:
        return jsonify({
            'success': False,
            'message': 'Kelime, anlamı zorunludur! 📝'
        })
    
    # Check if user is logged in
    user_id = session.get('user_id', None)
    
    if user_id:
        suggestion_user_id = user_id
        user = get_user_by_id(session['user_id'])
        success, result = add_suggestion(word, meaning, suggestion_user_id)
        
        # Yöneticiye e-posta bildirimi gönder
        new_word_suggestion_notification(word, meaning, user['username'])
    else:
        # Anonim öneriler için user_id None
        success, result = add_suggestion(word, meaning, None)
        
        # Yöneticiye anonim öneri için e-posta bildirimi gönder
        new_word_suggestion_notification(word, meaning, name if name else "Anonim Kullanıcı")
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Teşekkürler! Kelime öneriniz onay sürecine alındı. Onaylandıktan sonra sözlüğe eklenecektir. 🎉'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Bir hata oluştu. Lütfen daha sonra tekrar deneyin.'
        })

# Admin sayfaları
@app.route('/admin')
@admin_required
def admin_dashboard():
    user = get_user_by_id(session['user_id'])
    
    # İstatistikleri al
    pending_counts = get_pending_counts()
    total_words = get_total_words_count()
    total_users = get_total_users_count()
    today_words = get_words_added_today()
    month_words = get_words_added_this_month()
    
    return render_template('admin/dashboard.html', 
                           user=user, 
                           pending_suggestions=pending_counts['pending_suggestions'],
                           pending_edits=pending_counts['pending_edits'],
                           total_words=total_words,
                           total_users=total_users,
                           today_words=today_words,
                           month_words=month_words)

@app.route('/admin/suggestions')
@admin_required
def admin_suggestions():
    try:
        user = get_user_by_id(session['user_id'])
        pending_suggestions = get_pending_suggestions(limit=50)
        
        return render_template('admin/suggestions.html', 
                               user=user, 
                               suggestions=pending_suggestions)
    except Exception as e:
        # Hata logla
        print(f"Admin suggestions error: {str(e)}")
        # Hata sayfası göster
        flash(f'Bir hata oluştu: {str(e)}', 'error')
        return render_template('error.html', error=str(e))

@app.route('/admin/suggestion/approve/<int:suggestion_id>', methods=['POST'])
@admin_required
def admin_approve_suggestion(suggestion_id):
    success, result = approve_word(suggestion_id, session['user_id'])
    
    if success:
        flash('Kelime önerisi onaylandı ve sözlüğe eklendi.', 'success')
    else:
        flash(f'Onay sırasında bir hata oluştu: {result}', 'error')
        
    return redirect(url_for('admin_suggestions'))

@app.route('/admin/suggestion/reject/<int:suggestion_id>', methods=['POST'])
@admin_required
def admin_reject_suggestion(suggestion_id):
    admin_notes = request.form.get('admin_notes', '')
    success, result = reject_word(suggestion_id, session['user_id'], admin_notes)
    
    if success:
        flash('Kelime önerisi reddedildi.', 'success')
    else:
        flash(f'Red sırasında bir hata oluştu: {result}', 'error')
        
    return redirect(url_for('admin_suggestions'))

@app.route('/admin/edit-requests')
@admin_required
def admin_edit_requests():
    user = get_user_by_id(session['user_id'])
    pending_edits = get_pending_edit_requests(limit=50)
    
    return render_template('admin/edit_requests.html', 
                           user=user, 
                           edit_requests=pending_edits)

@app.route('/admin/edit-request/approve/<int:request_id>', methods=['POST'])
@admin_required
def admin_approve_edit_request(request_id):
    success, result = approve_edit_request(request_id, session['user_id'])
    
    if success:
        flash('Değişiklik talebi onaylandı ve kelime güncellendi.', 'success')
    else:
        flash(f'Onay sırasında bir hata oluştu: {result}', 'error')
        
    return redirect(url_for('admin_edit_requests'))

@app.route('/admin/edit-request/reject/<int:request_id>', methods=['POST'])
@admin_required
def admin_reject_edit_request(request_id):
    admin_notes = request.form.get('admin_notes', '')
    success, result = reject_edit_request(request_id, session['user_id'], admin_notes)
    
    if success:
        flash('Değişiklik talebi reddedildi.', 'success')
    else:
        flash(f'Red sırasında bir hata oluştu: {result}', 'error')
        
    return redirect(url_for('admin_edit_requests'))

# Kelime oylaması
@app.route('/vote', methods=['POST'])
@login_required
def vote():
    meaning_id = request.form.get('meaning_id')
    vote_type = request.form.get('vote_type')
    
    if not meaning_id or not vote_type:
        return jsonify({
            'success': False,
            'message': 'Eksik parametreler'
        })
        
    if vote_type not in ['up', 'down']:
        return jsonify({
            'success': False,
            'message': 'Geçersiz oy tipi'
        })
    
    # Burada oy verme işlemi gerçekleşiyor
    try:
        # vote_word fonksiyonu yoksa gerekli işlemi burada yapalım
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Veritabanı tipini kontrol et
        is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
        param_placeholder = get_param_placeholder(conn)
        
        # Önce meaning'in var olup olmadığını kontrol et
        query = f"SELECT id FROM words WHERE id = {param_placeholder}"
        cur.execute(query, (meaning_id,))
        
        if not cur.fetchone():
            return jsonify({
                'success': False,
                'message': 'Kelime bulunamadı'
            })
        
        # Oy ver
        if vote_type == 'up':
            query = f"UPDATE words SET votes_up = votes_up + 1 WHERE id = {param_placeholder}"
        else:
            query = f"UPDATE words SET votes_down = votes_down + 1 WHERE id = {param_placeholder}"
            
        cur.execute(query, (meaning_id,))
        conn.commit()
        
        # Güncel oy sayılarını al
        query = f"SELECT votes_up, votes_down FROM words WHERE id = {param_placeholder}"
        cur.execute(query, (meaning_id,))
        votes = cur.fetchone()
        
        if is_postgres:
            upvotes = votes['votes_up']
            downvotes = votes['votes_down']
        else:
            upvotes = votes[0]
            downvotes = votes[1]
        
        return jsonify({
            'success': True,
            'message': 'Oy başarıyla kaydedildi',
            'upvotes': upvotes,
            'downvotes': downvotes
        })
    except Exception as e:
        logger.error(f"Oy verme sırasında hata: {e}")
        return jsonify({
            'success': False,
            'message': 'Oy verilirken bir hata oluştu'
        })
    finally:
        if 'conn' in locals():
            conn.close()

# Düzenleme önerme sayfası
@app.route('/request-edit/<int:word_id>', methods=['GET'])
@login_required
def request_edit_form(word_id):
    # Kelimeyi getir
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Veritabanı tipini kontrol et
    is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
    param_placeholder = get_param_placeholder(conn)
    
    query = f"""
        SELECT w.*, u.username as suggested_by_username
        FROM words w
        LEFT JOIN users u ON w.suggested_by = u.id
        WHERE w.id = {param_placeholder}
    """
    
    cur.execute(query, (word_id,))
    word = cur.fetchone()
    conn.close()
    
    if not word:
        flash('Böyle bir kelime bulunamadı.', 'error')
        return redirect(url_for('index'))
    
    # Word nesnesini sözlüğe çevir
    if is_postgres:
        word_dict = dict(word)
    else:
        # SQLite için tuple'dan sözlüğe çevir
        columns = ['id', 'word', 'meaning', 'created_at', 'updated_at', 'suggested_by', 
                  'votes_up', 'votes_down', 'is_approved', 'approved_by', 'approved_at', 'suggested_by_username']
        word_dict = dict(zip(columns, word))
    
    return render_template('edit_request.html', word=word_dict)

# Düzenleme önerisi gönderme
@app.route('/request-edit/<int:word_id>', methods=['POST'])
@login_required
def submit_edit_request(word_id):
    new_meaning = request.form.get('new_meaning', '').strip()
    reason = request.form.get('reason', '').strip()
    
    if not new_meaning:
        flash('Yeni anlam alanı boş olamaz.', 'error')
        return redirect(url_for('request_edit_form', word_id=word_id))
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Veritabanı tipini kontrol et
        is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
        param_placeholder = get_param_placeholder(conn)
        
        # Önce edit_requests tablosunu kontrol et, yoksa oluştur
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS edit_requests (
                    id SERIAL PRIMARY KEY,
                    word_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    original_meaning TEXT NOT NULL,
                    new_meaning TEXT NOT NULL,
                    reason TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    admin_notes TEXT,
                    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            conn.commit()
        except Exception as e:
            logger.error(f"edit_requests tablosu oluşturulurken hata: {e}")
        
        # Önce kelimeyi getir
        query = f"SELECT meaning FROM words WHERE id = {param_placeholder}"
        cur.execute(query, (word_id,))
        word = cur.fetchone()
        
        if not word:
            flash('Böyle bir kelime bulunamadı.', 'error')
            return redirect(url_for('index'))
        
        original_meaning = word[0] if not is_postgres else word['meaning']
        
        # Düzenleme önerisini kaydet
        query = f"""
            INSERT INTO edit_requests 
            (word_id, user_id, original_meaning, new_meaning, reason, created_at, updated_at) 
            VALUES 
            ({param_placeholder}, {param_placeholder}, {param_placeholder}, {param_placeholder}, 
             {param_placeholder}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """
        
        cur.execute(query, (word_id, session['user_id'], original_meaning, new_meaning, reason))
        conn.commit()
        
        flash('Düzenleme öneriniz başarıyla alındı. Teşekkürler!', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Düzenleme önerisi gönderilirken hata: {e}")
        flash('Düzenleme önerisi gönderilirken bir hata oluştu.', 'error')
        return redirect(url_for('request_edit_form', word_id=word_id))
    finally:
        if 'conn' in locals():
            conn.close()

# Değişiklik talebi
@app.route('/request-edit/<int:word_id>', methods=['POST'])
@login_required
def edit_request(word_id):
    new_meaning = request.form.get('new_meaning', '').strip()
    reason = request.form.get('reason', '').strip()
    
    if not new_meaning:
        return jsonify({
            'success': False,
            'message': 'Yeni anlam zorunludur!'
        })
    
    success, result = request_edit(word_id, new_meaning, reason, session['user_id'])
    
    if success:
        # Değişiklik talebi için yöneticiye e-posta gönder
        word_info = get_word(word_id)
        user = get_user_by_id(session['user_id'])
        if word_info and user:
            edit_request_notification(word_info[0]['word'], word_info[0]['meaning'], new_meaning, reason, user['username'])
        
        return jsonify({
            'success': True,
            'message': 'Değişiklik talebiniz alındı. İncelendikten sonra onaylanacaktır.'
        })
    else:
        return jsonify({
            'success': False,
            'message': f'Bir hata oluştu: {result}'
        })

# SSL için context oluşturma fonksiyonu - Cloudflare kullanıldığı için devre dışı
def create_ssl_context():
    # Cloudflare SSL yönettiği için kendi SSL'imizi kullanmıyoruz
    print("Cloudflare SSL kullanıldığı için yerel SSL devre dışı.")
    return None

# Custom template filter for safe date formatting
@app.template_filter('safe_date')
def safe_date_filter(value, format='%d/%m/%Y %H:%M'):
    """Safely format a date value, handling both datetime objects and strings."""
    if value is None:
        return "Belirtilmemiş"
    
    if isinstance(value, datetime):
        return value.strftime(format)
    
    if isinstance(value, str):
        try:
            # Try to parse the string as a datetime
            date_obj = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            return date_obj.strftime(format)
        except (ValueError, TypeError):
            # If parsing fails, return the original string
            return value
    
    # For any other type, return as string
    return str(value)

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    port = int(os.environ.get('PORT', 5000))
    
    # Railway için host ve port ayarı
    print(f"Uygulama {port} numaralı portta başlatılıyor...")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
