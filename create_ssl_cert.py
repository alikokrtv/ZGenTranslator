"""
SSL sertifikası oluşturma scripti
"""
from OpenSSL import crypto
import os

def create_self_signed_cert():
    # Sertifika ve anahtar dosya yolları
    cert_file = "ssl/cert.pem"
    key_file = "ssl/key.pem"
    
    # SSL klasörü yoksa oluştur
    if not os.path.exists("ssl"):
        os.makedirs("ssl")
    
    # Eğer sertifika ve anahtar zaten varsa tekrar oluşturma
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print("Sertifika ve anahtar dosyaları zaten mevcut.")
        return
    
    # Yeni bir anahtar çifti oluştur
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)
    
    # Sertifika oluştur
    cert = crypto.X509()
    cert.get_subject().C = "TR"  # Ülke
    cert.get_subject().ST = "Istanbul"  # Şehir
    cert.get_subject().L = "Istanbul"  # Konum
    cert.get_subject().O = "Z Kusagi Translator"  # Organizasyon
    cert.get_subject().OU = "Web"  # Organizasyon birimi
    cert.get_subject().CN = "localhost"  # Common Name
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10*365*24*60*60)  # 10 yıl geçerli
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha256')
    
    # Dosyalara yaz
    with open(cert_file, "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    
    with open(key_file, "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
    
    print(f"Self-signed sertifika oluşturuldu: {cert_file}")
    print(f"Private key oluşturuldu: {key_file}")

if __name__ == "__main__":
    create_self_signed_cert()
