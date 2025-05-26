"""
E-posta Bildirimleri Sistemi
Bu modül, Z Kuşağı Translator için e-posta bildirimleri gönderir.
"""
from flask import Flask
from flask_mail import Mail, Message
import os

# E-posta konfigürasyonu
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USE_SSL": False,
    "MAIL_USERNAME": 'alikokrtv@gmail.com',
    "MAIL_PASSWORD": 'chez obrp ugyl lfgn',  # Gmail App Password
    "MAIL_DEFAULT_SENDER": 'alikokrtv@gmail.com'
}

mail = Mail()

def init_mail(app):
    """Mail sistemini başlat"""
    app.config.update(mail_settings)
    mail.init_app(app)
    return mail

def send_notification(subject, recipient, template):
    """
    E-posta bildirimi gönder
    
    Args:
        subject (str): E-posta konusu
        recipient (str): Alıcı e-posta adresi
        template (str): E-posta içeriği (HTML)
    """
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            html=template,
            sender=mail_settings["MAIL_DEFAULT_SENDER"]
        )
        mail.send(msg)
        return True, "E-posta başarıyla gönderildi"
    except Exception as e:
        return False, f"E-posta gönderilirken hata oluştu: {str(e)}"

def password_reset_notification(email, username, reset_link):
    """Kullanıcıya şifre sıfırlama bağlantısı gönder"""
    subject = "Z Kuşağı Çevirici - Şifre Sıfırlama"
    
    html_template = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e5e5e5; border-radius: 5px;">
        <h2 style="color: #7C3AED; margin-bottom: 20px;">Z Kuşağı Çevirici - Şifre Sıfırlama</h2>
        <p>Merhaba <strong>{username}</strong>,</p>
        <p>Şifrenizi sıfırlamak için bir istek aldık. Aşağıdaki bağlantıya tıklayarak yeni bir şifre oluşturabilirsiniz:</p>
        <p style="margin: 30px 0; text-align: center;">
            <a href="{reset_link}" style="background-color: #7C3AED; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; font-weight: bold;">Şifremi Sıfırla</a>
        </p>
        <p>Eğer bu isteği siz yapmadıysanız, bu e-postayı görmezden gelebilirsiniz. Hesabınız güvende.</p>
        <p>Not: Bu bağlantı 24 saat boyunca geçerlidir.</p>
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e5e5;">
        <p style="color: #666; font-size: 12px; text-align: center;">
            &copy; Z Kuşağı Çevirici | Bu otomatik bir e-postadır, lütfen yanıtlamayın.
        </p>
    </div>
    """
    
    return send_notification(subject, email, html_template)

def new_word_suggestion_notification(word, meaning, submitter=None):
    """Yeni kelime önerisi bildirimini yöneticiye gönder"""
    subject = f"Yeni Kelime Önerisi: {word}"
    
    if submitter:
        submitter_text = f"<p><strong>Öneren:</strong> {submitter}</p>"
    else:
        submitter_text = "<p><strong>Öneren:</strong> Anonim Kullanıcı</p>"
    
    template = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #7C3AED; color: white; padding: 10px 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 20px; border-radius: 0 0 5px 5px; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Z Kuşağı Translator - Yeni Kelime Önerisi</h2>
                </div>
                <div class="content">
                    <p>Merhaba,</p>
                    <p>Z Kuşağı Translator'e yeni bir kelime önerisi yapıldı:</p>
                    <p><strong>Kelime:</strong> {word}</p>
                    <p><strong>Anlam:</strong> {meaning}</p>
                    {submitter_text}
                    <p>Bu öneriyi incelemek ve onaylamak için admin paneline giriş yapabilirsiniz.</p>
                </div>
                <div class="footer">
                    <p>Bu e-posta Z Kuşağı Translator sistemi tarafından otomatik olarak gönderilmiştir.</p>
                </div>
            </div>
        </body>
    </html>
    """
    
    return send_notification(subject, mail_settings["MAIL_USERNAME"], template)

def edit_request_notification(word, current_meaning, new_meaning, reason, username):
    """Kelime düzenleme talebi bildirimini yöneticiye gönder"""
    subject = f"Kelime Düzenleme Talebi: {word}"
    
    template = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #7C3AED; color: white; padding: 10px 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 20px; border-radius: 0 0 5px 5px; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #777; }}
                .changes {{ background-color: #e9f5ff; padding: 10px; border-left: 4px solid #0077cc; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Z Kuşağı Translator - Kelime Düzenleme Talebi</h2>
                </div>
                <div class="content">
                    <p>Merhaba,</p>
                    <p>Z Kuşağı Translator'de bir kelime için düzenleme talebi geldi:</p>
                    <p><strong>Kelime:</strong> {word}</p>
                    <div class="changes">
                        <p><strong>Mevcut Anlam:</strong> {current_meaning}</p>
                        <p><strong>Önerilen Anlam:</strong> {new_meaning}</p>
                    </div>
                    <p><strong>Değişiklik Sebebi:</strong> {reason}</p>
                    <p><strong>Talep Eden:</strong> {username}</p>
                    <p>Bu talebi incelemek ve onaylamak için admin paneline giriş yapabilirsiniz.</p>
                </div>
                <div class="footer">
                    <p>Bu e-posta Z Kuşağı Translator sistemi tarafından otomatik olarak gönderilmiştir.</p>
                </div>
            </div>
        </body>
    </html>
    """
    
    return send_notification(subject, mail_settings["MAIL_USERNAME"], template)

def user_registration_notification(username, email):
    """Yeni kullanıcı kaydı bildirimini yöneticiye gönder"""
    subject = f"Yeni Kullanıcı Kaydı: {username}"
    
    template = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #7C3AED; color: white; padding: 10px 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 20px; border-radius: 0 0 5px 5px; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Z Kuşağı Translator - Yeni Kullanıcı Kaydı</h2>
                </div>
                <div class="content">
                    <p>Merhaba,</p>
                    <p>Z Kuşağı Translator'e yeni bir kullanıcı kaydoldu:</p>
                    <p><strong>Kullanıcı Adı:</strong> {username}</p>
                    <p><strong>E-posta:</strong> {email}</p>
                    <p>Artık platformumuzda {username} adıyla katkıda bulunabilecek.</p>
                </div>
                <div class="footer">
                    <p>Bu e-posta Z Kuşağı Translator sistemi tarafından otomatik olarak gönderilmiştir.</p>
                </div>
            </div>
        </body>
    </html>
    """
    
    return send_notification(subject, mail_settings["MAIL_USERNAME"], template)
