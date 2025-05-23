"""
Passenger WSGI Uygulaması
Bu dosya, Natro hosting gibi Passenger kullanan sunucular için WSGI yapılandırmasını içerir.
"""

import sys
import os
import logging
import traceback

# Loglama yapılandırması
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'error.log')
logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)

logging.info('--------- Uygulama başlatılıyor ---------')

try:
    # Modül yolunu ekle - Python yolu sorunu olabilir
    # Natro hosting için doğru Python yolunu kullan
    # Eğer bu satır hata veriyorsa, doğru yolu Natro desteğinden öğrenin
    INTERP = os.path.expanduser("/usr/local/bin/python3.9")
    if sys.executable != INTERP:
        try:
            os.execl(INTERP, INTERP, *sys.argv)
        except Exception as e:
            logging.error(f"Python yorumlayıcı hatası: {str(e)}")
            # Hata oluştuğunda devam et, sistemin varsayılan Python'ını kullan

    # Mevcut dizini Python yoluna ekle
    current_dir = os.getcwd()
    logging.info(f"Çalışma dizini: {current_dir}")
    sys.path.append(current_dir)

    # SQLite veritabanı yolu - Debugging için
    db_path = os.path.join(current_dir, 'zgen_translator.db')
    logging.info(f"Veritabanı yolu: {db_path}")
    if os.path.exists(db_path):
        logging.info("Veritabanı dosyası mevcut")
    else:
        logging.error("Veritabanı dosyası bulunamadı!")

    # Flask uygulamasını içe aktar
    logging.info("Flask uygulaması içe aktarılıyor...")
    from app import app as application
    logging.info("Flask uygulaması başarıyla içe aktarıldı")

except Exception as e:
    logging.error(f"Kritik hata: {str(e)}")
    logging.error(traceback.format_exc())
    
    # Basit bir hata sayfası gösteren fonksiyon
    def application(environ, start_response):
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/plain; charset=utf-8')]
        start_response(status, response_headers)
        error_msg = f"Uygulama başlatılırken bir hata oluştu. Lütfen daha sonra tekrar deneyin. Hata: {str(e)}".encode('utf-8')
        return [error_msg]
