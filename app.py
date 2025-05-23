import os
import json
import hashlib
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, abort, request
from models import (init_db, get_word, add_word, add_suggestion, get_popular_words, 
                  register_user, get_user_by_username, get_user_by_id, get_user_achievements, 
                  get_user_words, get_top_contributors, is_admin, get_pending_suggestions,
                  approve_word, reject_word, request_edit, get_pending_edit_requests,
                  approve_edit_request, reject_edit_request, vote_word, get_total_words_count,
                  get_total_users_count, get_words_added_today, get_words_added_this_month,
                  get_pending_counts)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "z-kusagi-translator-secret")

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

# Initialize database
init_db()

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
    user = None
    is_user_admin = False
    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
        is_user_admin = is_admin(session['user_id'])
    top_contributors = get_top_contributors(5)
    return render_template('index.html', user=user, top_contributors=top_contributors, is_admin=is_user_admin)

@app.route('/popular', methods=['GET'])
def popular_words():
    words = get_popular_words(10)
    return jsonify({
        'success': True,
        'words': words
    })

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
            flash('Kayıt başarılı! Hoş geldiniz.', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Kayıt sırasında bir hata oluştu. Lütfen tekrar deneyin.', 'error')
            
    return render_template('register.html')

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('profile'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Kullanıcı adı ve şifre gereklidir.', 'error')
            return render_template('login.html')
            
        # Get user
        user = get_user_by_username(username)
        
        if not user:
            flash('Kullanıcı adı veya şifre hatalı.', 'error')
            return render_template('login.html')
            
        # Check password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if user['password_hash'] != password_hash:
            flash('Kullanıcı adı veya şifre hatalı.', 'error')
            return render_template('login.html')
            
        # Login successful
        session['user_id'] = user['id']
        flash('Giriş başarılı! Hoş geldiniz.', 'success')
        
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('profile'))
        
    return render_template('login.html')

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
    
    if results:
        # Format results for the frontend
        formatted_results = []
        for result in results:
            contributor = None
            if result.get('suggested_by'):
                user = get_user_by_id(result['suggested_by'])
                if user:
                    contributor = user['username']
            
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
            'user': user_info['username'] if user_info else None
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
    
    # Önerilen kelime onay sürecine gönderilir
    suggestion_id = add_word(word, meaning, user_id)
    
    if user_id:
        print(f"Yeni kelime önerisi: '{word}' = '{meaning}' (Kullanıcı ID: {user_id})")
    else:
        print(f"Yeni kelime önerisi: '{word}' = '{meaning}' (Öneren: {name if name else 'İsimsiz'})")
    
    if suggestion_id:
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
    user = get_user_by_id(session['user_id'])
    pending_suggestions = get_pending_suggestions(limit=50)
    
    return render_template('admin/suggestions.html', 
                           user=user, 
                           suggestions=pending_suggestions)

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
@app.route('/vote/<int:word_id>/<vote_type>', methods=['POST'])
@login_required
def vote(word_id, vote_type):
    if vote_type not in ['up', 'down']:
        return jsonify({
            'success': False,
            'message': 'Geçersiz oy tipi'
        })
    
    success, message = vote_word(word_id, session['user_id'], vote_type)
    
    return jsonify({
        'success': success,
        'message': message
    })

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

if __name__ == '__main__':
    ssl_context = create_ssl_context()
    debug_mode = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    
    if ssl_context:
        app.run(host='0.0.0.0', port=5000, debug=debug_mode, ssl_context=ssl_context)
    else:
        # Eğer SSL context yoksa, normal HTTP ile çalıştır
        print("SSL sertifikası olmadan çalışılıyor. Güvenli bağlantı için sertifika oluşturun.")
        app.run(host='0.0.0.0', port=5000, debug=debug_mode)
