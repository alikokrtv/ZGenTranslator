"""
Passenger WSGI Uygulaması
Bu dosya, Natro hosting gibi Passenger kullanan sunucular için WSGI yapılandırmasını içerir.
"""

import sys
import os

# Modül yolunu ekle
INTERP = os.path.expanduser("/usr/local/bin/python3.9")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Mevcut dizini Python yoluna ekle
sys.path.append(os.getcwd())

# Flask uygulamasını içe aktar
from app import app as application
