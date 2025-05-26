#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import hashlib
import datetime
from db_config import get_db_connection
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('seed_database')

def hash_password(password):
    """SHA-256 ile şifre hashleme"""
    return hashlib.sha256(password.encode()).hexdigest()

def seed_admin_user():
    """Admin kullanıcısı oluştur"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Veritabanı tipini kontrol et
    is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
    param_placeholder = '%s' if is_postgres else '?'
    
    try:
        # Önce admin kullanıcısının var olup olmadığını kontrol et
        query = f"""
            SELECT id FROM users 
            WHERE username = {param_placeholder} OR email = {param_placeholder}
        """
        cur.execute(query, ('admin', 'admin@zgentranslator.com'))
        existing_admin = cur.fetchone()
        
        if existing_admin:
            logger.info('Admin kullanıcısı zaten var.')
        else:
            # Admin kullanıcısı oluştur
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            admin_password = hash_password('admin123')
            
            query = f"""
                INSERT INTO users (username, email, password, role, created_at, updated_at, is_active, points)
                VALUES ({param_placeholder}, {param_placeholder}, {param_placeholder}, {param_placeholder}, 
                        {param_placeholder}, {param_placeholder}, {param_placeholder}, {param_placeholder})
                RETURNING id
            """
            
            cur.execute(query, ('admin', 'admin@zgentranslator.com', admin_password, 
                               'admin', now, now, True, 1000))
            
            admin_id = cur.fetchone()[0] if is_postgres else cur.lastrowid
            conn.commit()
            logger.info(f'Admin kullanıcısı başarıyla oluşturuldu! ID: {admin_id}')
            logger.info('Kullanıcı adı: admin, Şifre: admin123')
            
            return admin_id
    except Exception as e:
        logger.error(f'Admin kullanıcısı oluşturulurken hata: {e}')
        conn.rollback()
        return None
    finally:
        conn.close()

def seed_sample_words(admin_id=None):
    """Örnek Z kuşağı terimleri ekle"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Veritabanı tipini kontrol et
    is_postgres = hasattr(conn, 'cursor_factory') or 'psycopg2' in str(type(conn))
    param_placeholder = '%s' if is_postgres else '?'
    
    # Örnek Z kuşağı terimleri
    sample_words = [
        {'word': 'cringe', 'meaning': 'Utanç verici, garip veya rahatsız edici bir durum'},
        {'word': 'based', 'meaning': 'Kendine güvenen, sağlam duruşlu, kendi fikrini çekinmeden söyleyen'},
        {'word': 'no cap', 'meaning': 'Yalan yok, cidden, gerçekten'},
        {'word': 'slay', 'meaning': 'Çok iyi yapmak, harika görünmek, etkilemek'},
        {'word': 'rizz', 'meaning': 'Karizma, çekicilik, flört etme yeteneği'},
        {'word': 'vibe check', 'meaning': 'Ortamın veya kişinin enerjisini/havasını kontrol etmek'},
        {'word': 'simp', 'meaning': 'Birine aşırı ilgi göstermek, yüz suyu dökmek'},
        {'word': 'sus', 'meaning': 'Şüpheli, güvenilmez (suspicious kelimesinin kısaltması)'},
        {'word': 'main character energy', 'meaning': 'Hayatı ana karakter gibi yaşama hissi, özgüven'},
        {'word': 'mid', 'meaning': 'Ortalama, vasat, beklentiyi karşılamayan'},
        {'word': 'yeet', 'meaning': 'Bir şeyi güçlü ve hızlı bir şekilde fırlatmak'},
        {'word': 'GOAT', 'meaning': 'En iyisi, tüm zamanların en iyisi (Greatest Of All Time)'},
        {'word': 'drip', 'meaning': 'Çok şık, havalı giyim tarzı'},
        {'word': 'lit', 'meaning': 'Harika, çok eğlenceli, heyecan verici'},
        {'word': 'FOMO', 'meaning': 'Bir şeyleri kaçırma korkusu (Fear Of Missing Out)'},
        {'word': 'ghosting', 'meaning': 'Birisiyle iletişimi aniden ve tamamen kesmek'},
        {'word': 'lowkey', 'meaning': 'Gizlice, sessizce, çok belli etmeden'},
        {'word': 'highkey', 'meaning': 'Açıkça, belli bir şekilde, herkesin görebileceği şekilde'},
        {'word': 'L', 'meaning': 'Başarısızlık, kayıp (Loss kelimesinin kısaltması)'},
        {'word': 'W', 'meaning': 'Başarı, kazanç (Win kelimesinin kısaltması)'},
    ]
    
    try:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        inserted_count = 0
        
        for word_data in sample_words:
            # Kelimenin zaten var olup olmadığını kontrol et
            query = f"""
                SELECT id FROM words 
                WHERE word = {param_placeholder}
            """
            cur.execute(query, (word_data['word'],))
            existing_word = cur.fetchone()
            
            if existing_word:
                logger.info(f"'{word_data['word']}' kelimesi zaten var, atlanıyor.")
                continue
            
            # Kelimeyi ekle
            if is_postgres:
                query = f"""
                    INSERT INTO words (word, meaning, created_at, updated_at, 
                                     suggested_by, votes_up, votes_down, is_approved, approved_by, approved_at)
                    VALUES ({param_placeholder}, {param_placeholder}, {param_placeholder}, {param_placeholder}, 
                            {param_placeholder}, {param_placeholder}, {param_placeholder}, {param_placeholder}, 
                            {param_placeholder}, {param_placeholder})
                """
            else:
                query = f"""
                    INSERT INTO words (word, meaning, created_at, updated_at, 
                                     suggested_by, votes_up, votes_down, is_approved, approved_by, approved_at)
                    VALUES ({param_placeholder}, {param_placeholder}, {param_placeholder}, {param_placeholder}, 
                            {param_placeholder}, {param_placeholder}, {param_placeholder}, {param_placeholder}, 
                            {param_placeholder}, {param_placeholder})
                """
            
            # Her kelime için rastgele upvote değeri (1-50 arası)
            import random
            upvotes = random.randint(1, 50)
            downvotes = random.randint(0, 10)
            
            cur.execute(query, (
                word_data['word'], 
                word_data['meaning'],
                now,
                now,
                admin_id,  # admin kullanıcısı tarafından önerildi
                upvotes,  # rastgele upvote
                downvotes,  # rastgele downvote
                1,  # onaylandı
                admin_id,  # admin tarafından onaylandı
                now  # şu an onaylandı
            ))
            
            inserted_count += 1
        
        conn.commit()
        logger.info(f'{inserted_count} adet Z kuşağı terimi başarıyla eklendi!')
    except Exception as e:
        logger.error(f'Örnek terimler eklenirken hata: {e}')
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    logger.info("Veritabanı seed işlemi başlatılıyor...")
    admin_id = seed_admin_user()
    seed_sample_words(admin_id)
    logger.info("Veritabanı seed işlemi tamamlandı!")
