import sqlite3
import hashlib
import random
from datetime import datetime, timedelta

# Veritabanı bağlantısı
DB_PATH = 'zgen_translator.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def add_sample_users():
    """Örnek kullanıcıları ekle"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Önce kullanıcı sayısını kontrol et
    cur.execute("SELECT COUNT(*) FROM users")
    user_count = cur.fetchone()[0]
    
    if user_count < 3:  # Sadece birkaç kullanıcı varsa örnek kullanıcılar ekle
        print("Örnek kullanıcılar ekleniyor...")
        
        sample_users = [
            ("zgen_master", "zgen_master@example.com", hashlib.sha256("password123".encode()).hexdigest(), 35, 1),
            ("ayse_z", "ayse@example.com", hashlib.sha256("password123".encode()).hexdigest(), 25, 0),
            ("mehmet_z", "mehmet@example.com", hashlib.sha256("password123".encode()).hexdigest(), 20, 0),
            ("zeynep_kusagi", "zeynep@example.com", hashlib.sha256("password123".encode()).hexdigest(), 15, 0),
            ("ali_translator", "ali@example.com", hashlib.sha256("password123".encode()).hexdigest(), 18, 0),
            ("z_kuşağı_fan", "zfan@example.com", hashlib.sha256("password123".encode()).hexdigest(), 10, 0),
            ("gen_z_lover", "genz@example.com", hashlib.sha256("password123".encode()).hexdigest(), 12, 0),
            ("kusak_expert", "expert@example.com", hashlib.sha256("password123".encode()).hexdigest(), 8, 0)
        ]
        
        for user in sample_users:
            try:
                cur.execute("""
                    INSERT INTO users (username, email, password_hash, contribution_count, is_admin) 
                    VALUES (?, ?, ?, ?, ?)
                """, user)
                print(f"Kullanıcı eklendi: {user[0]}")
            except sqlite3.IntegrityError:
                print(f"Kullanıcı zaten var: {user[0]}")
        
        conn.commit()
        print(f"{len(sample_users)} örnek kullanıcı eklendi veya güncellendi.")
    else:
        print(f"Zaten {user_count} kullanıcı var, örnek kullanıcı eklemiyorum.")
    
    conn.close()

def add_sample_words_and_votes():
    """Örnek kelimeler ve oylar ekle"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Kullanıcı ID'lerini al
    cur.execute("SELECT id FROM users")
    user_ids = [row['id'] for row in cur.fetchall()]
    
    if not user_ids:
        print("Önce örnek kullanıcılar ekleyin.")
        conn.close()
        return
    
    # Yeni Z kuşağı kelimeleri
    new_words = [
        ("periodt", "Bir tartışmayı bitirmek için kullanılan ifade, nokta koyuyorum anlamında"),
        ("slay", "Çok iyi bir iş çıkarmak, etkileyici olmak"),
        ("main character energy", "Kendini bir filmin/dizinin ana karakteri gibi hissetmek"),
        ("rent free", "Birisinin aklından çıkmayan düşünce"),
        ("rizz", "Flört yeteneği, karşı cinsi etkileme becerisi"),
        ("pov", "Bakış açısı (point of view)"),
        ("skibidi", "Kendini ifade etmek için kullanılan anlamsız bir kelime"),
        ("gyat", "Şaşkınlık, hayranlık ifadesi"),
        ("mid", "Vasat, ortalama, sıradan"),
        ("ick", "Birinden soğuma sebebi"),
        ("core", "Bir tarzı, estetiği belirtmek için kullanılır (softcore, corecore vb.)"),
        ("szn", "Sezon (season) kelimesinin kısaltması"),
        ("bussin", "Çok iyi, harika, mükemmel"),
        ("glow up", "Fiziksel veya kişisel olarak olumlu değişim geçirmek"),
        ("sheesh", "Şaşkınlık, hayranlık ifadesi")
    ]
    
    # Kelimeleri ekle ve rastgele oy ver
    for word, meaning in new_words:
        # Önce kelimenin var olup olmadığını kontrol et
        cur.execute("SELECT id FROM words WHERE word = ?", (word,))
        existing_word = cur.fetchone()
        
        word_id = None
        
        if existing_word:
            word_id = existing_word['id']
            print(f"Kelime zaten var: {word}")
        else:
            # Rastgele bir kullanıcı tarafından önerilmiş gibi yap
            suggested_by = random.choice(user_ids)
            approved_by = user_ids[0]  # İlk kullanıcı admin olarak kabul edilir
            
            # Rastgele bir geçmiş tarih belirle (son 30 gün içinde)
            days_ago = random.randint(1, 30)
            created_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                cur.execute("""
                    INSERT INTO words (word, meaning, suggested_by, is_approved, approved_by, approved_at, created_at, votes_up, votes_down) 
                    VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?)
                """, (word, meaning, suggested_by, approved_by, created_date, created_date, random.randint(0, 50), random.randint(0, 5)))
                
                word_id = cur.lastrowid
                print(f"Kelime eklendi: {word}")
                
                # Kullanıcının contribution_count'unu artır
                cur.execute("UPDATE users SET contribution_count = contribution_count + 1 WHERE id = ?", (suggested_by,))
            except sqlite3.IntegrityError:
                print(f"Kelime eklenirken hata: {word}")
        
        # Rastgele oylar ekle (kelime zaten varsa veya yeni eklendiyse)
        if word_id:
            # Kullanıcıların 30-70%'si oy versin
            voter_count = int(len(user_ids) * (random.randint(30, 70) / 100))
            voters = random.sample(user_ids, min(voter_count, len(user_ids)))
            
            for voter_id in voters:
                # 80% ihtimalle olumlu oy, 20% ihtimalle olumsuz oy
                vote_type = "up" if random.random() < 0.8 else "down"
                vote_column = "votes_up" if vote_type == "up" else "votes_down"
                
                # Oyları artır
                cur.execute(f"UPDATE words SET {vote_column} = {vote_column} + 1 WHERE id = ?", (word_id,))
    
    conn.commit()
    print(f"{len(new_words)} kelime ve oylar eklendi veya güncellendi.")
    conn.close()

def add_sample_pending_suggestions():
    """Örnek bekleyen öneriler ekle"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Kullanıcı ID'lerini al
    cur.execute("SELECT id FROM users WHERE is_admin = 0")  # Admin olmayanlar
    user_ids = [row['id'] for row in cur.fetchall()]
    
    if not user_ids:
        print("Önce örnek kullanıcılar ekleyin.")
        conn.close()
        return
    
    # Bekleyen öneri sayısını kontrol et
    cur.execute("SELECT COUNT(*) FROM suggestions WHERE status = 'pending'")
    pending_count = cur.fetchone()[0]
    
    if pending_count < 5:  # Eğer 5'ten az bekleyen öneri varsa
        # Yeni bekleyen öneriler
        pending_suggestions = [
            ("siuuu", "Sevinç, kutlama anında kullanılan bir ifade"),
            ("W rizz", "Mükemmel flört yeteneği"),
            ("no cap", "Yalan söylemiyorum, ciddiyim"),
            ("chief", "Arkadaş, dostum anlamında kullanılır"),
            ("lowkey", "Gizlice, sessizce bir şeyi sevmek veya yapmak")
        ]
        
        for word, meaning in pending_suggestions:
            # Önce önerinin var olup olmadığını kontrol et
            cur.execute("SELECT id FROM suggestions WHERE word = ? AND status = 'pending'", (word,))
            existing = cur.fetchone()
            
            if not existing:
                # Rastgele bir kullanıcı tarafından önerilmiş gibi yap
                suggested_by = random.choice(user_ids)
                
                # Rastgele bir tarih (son 7 gün içinde)
                days_ago = random.randint(1, 7)
                created_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
                
                try:
                    cur.execute("""
                        INSERT INTO suggestions (word, meaning, suggested_by, created_at, status) 
                        VALUES (?, ?, ?, ?, 'pending')
                    """, (word, meaning, suggested_by, created_date))
                    print(f"Bekleyen öneri eklendi: {word}")
                except sqlite3.IntegrityError:
                    print(f"Öneri eklenirken hata: {word}")
        
        conn.commit()
        print(f"{len(pending_suggestions)} bekleyen öneri eklendi veya güncellendi.")
    else:
        print(f"Zaten {pending_count} bekleyen öneri var, yeni öneri eklemiyorum.")
    
    conn.close()

def add_sample_edit_requests():
    """Örnek düzenleme talepleri ekle"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Kullanıcı ID'lerini al
    cur.execute("SELECT id FROM users WHERE is_admin = 0")  # Admin olmayanlar
    user_ids = [row['id'] for row in cur.fetchall()]
    
    if not user_ids:
        print("Önce örnek kullanıcılar ekleyin.")
        conn.close()
        return
    
    # Mevcut kelimeleri al
    cur.execute("SELECT id, meaning FROM words ORDER BY RANDOM() LIMIT 5")
    words = cur.fetchall()
    
    if not words:
        print("Önce örnek kelimeler ekleyin.")
        conn.close()
        return
    
    # Bekleyen düzenleme taleplerini kontrol et
    cur.execute("SELECT COUNT(*) FROM edit_requests WHERE status = 'pending'")
    pending_count = cur.fetchone()[0]
    
    if pending_count < 5:  # Eğer 5'ten az bekleyen düzenleme talebi varsa
        for word in words:
            # Rastgele bir kullanıcı seç
            requested_by = random.choice(user_ids)
            
            # Mevcut anlamı değiştir
            current_meaning = word['meaning']
            new_meaning = current_meaning + " (Z kuşağı arasında daha yaygın kullanılır)"
            
            # Rastgele bir neden
            reasons = [
                "Anlam tam olarak açıklanmamış",
                "Daha modern bir tanım gerekiyor",
                "Bu kelime artık farklı anlamda kullanılıyor",
                "Anlamı güncellemek gerekiyor",
                "Bu daha doğru bir açıklama"
            ]
            reason = random.choice(reasons)
            
            # Rastgele bir tarih (son 7 gün içinde)
            days_ago = random.randint(1, 7)
            created_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                cur.execute("""
                    INSERT INTO edit_requests (word_id, new_meaning, reason, requested_by, created_at, status) 
                    VALUES (?, ?, ?, ?, ?, 'pending')
                """, (word['id'], new_meaning, reason, requested_by, created_date))
                print(f"Düzenleme talebi eklendi: word_id={word['id']}")
            except sqlite3.IntegrityError:
                print(f"Düzenleme talebi eklenirken hata: word_id={word['id']}")
    
        conn.commit()
        print(f"{len(words)} düzenleme talebi eklendi veya güncellendi.")
    else:
        print(f"Zaten {pending_count} bekleyen düzenleme talebi var, yeni talep eklemiyorum.")
    
    conn.close()

def add_user_achievements():
    """Kullanıcılara başarımlar ekle"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Başarımları al
    cur.execute("SELECT id, requirement_count FROM achievements")
    achievements = cur.fetchall()
    
    # Kullanıcıları al
    cur.execute("SELECT id, contribution_count FROM users")
    users = cur.fetchall()
    
    for user in users:
        user_id = user['id']
        contribution_count = user['contribution_count']
        
        for achievement in achievements:
            achievement_id = achievement['id']
            requirement_count = achievement['requirement_count']
            
            if contribution_count >= requirement_count:
                # Kullanıcının bu başarımı var mı kontrol et
                cur.execute("""
                    SELECT 1 FROM user_achievements 
                    WHERE user_id = ? AND achievement_id = ?
                """, (user_id, achievement_id))
                
                if not cur.fetchone():
                    # Rastgele bir tarih (son 30 gün içinde)
                    days_ago = random.randint(1, 30)
                    earned_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
                    
                    try:
                        cur.execute("""
                            INSERT INTO user_achievements (user_id, achievement_id, earned_at) 
                            VALUES (?, ?, ?)
                        """, (user_id, achievement_id, earned_date))
                        print(f"Başarım eklendi: user_id={user_id}, achievement_id={achievement_id}")
                    except sqlite3.IntegrityError:
                        print(f"Başarım eklenirken hata: user_id={user_id}, achievement_id={achievement_id}")
    
    conn.commit()
    print("Kullanıcı başarımları güncellendi.")
    conn.close()

if __name__ == "__main__":
    print("Örnek veri ekleme başlıyor...")
    add_sample_users()
    add_sample_words_and_votes()
    add_sample_pending_suggestions()
    add_sample_edit_requests()
    add_user_achievements()
    print("Örnek veri ekleme tamamlandı!")
