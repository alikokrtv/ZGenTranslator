from app import app  # noqa: F401

if __name__ == "__main__":
    # Önbellek sorunlarını önlemek için ayarlar
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Statik dosyaların önbelleğe alınmasını engelle
    app.config['TEMPLATES_AUTO_RELOAD'] = True  # Şablonları otomatik yeniden yükle
    
    app.run(host="0.0.0.0", port=5000, debug=True)
