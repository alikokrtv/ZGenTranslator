"""
WSGI Uygulaması
Bu dosya, Natro gibi hosting sağlayıcıları için WSGI uygulamasını tanımlar.
"""

import os
import sys

# Modül yolunu ekleyin
sys.path.insert(0, os.path.dirname(__file__))

# Flask uygulamasını içe aktarın
from app import app as application

# Bu bir WSGI dosyasıdır - Flask uygulamasını application olarak dışa aktarır
if __name__ == '__main__':
    # Geliştirme ortamında doğrudan çalışıyorsa SSL kullan
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
