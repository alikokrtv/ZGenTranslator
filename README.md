# ZGenTranslator

Z Kuşağı Tercümanı - Z jenerasyonunun kullandığı terimleri açıklayan çevrimiçi sözlük.

## Railway Deployment

Bu uygulama Railway platformunda çalışacak şekilde yapılandırılmıştır.

### Railway'e Deployment Adımları

1. [Railway.app](https://railway.app) hesabı oluşturun
2. Yeni bir proje oluşturun
3. GitHub reponuzu bağlayın veya kodu doğrudan yükleyin
4. Aşağıdaki çevre değişkenlerini ayarlayın:
   - `SESSION_SECRET`: Güvenli bir rastgele dize
   - `FLASK_DEBUG`: Production için "False"
   - `FLASK_ENV`: "production"
   
### Veritabanı
   
Varsayılan olarak uygulama SQLite kullanır, ancak Railway'in PostgreSQL veritabanını kullanmanız önerilir:

1. Railway kontrol panelinden "New" → "Database" → "PostgreSQL" seçin
2. PostgreSQL veritabanı eklendikten sonra, uygulamanızda `DATABASE_URL` çevre değişkeni otomatik olarak ayarlanacaktır
3. Eğer PostgreSQL kullanmak isterseniz, models.py dosyasını güncellemeniz gerekecektir

### Özel Alan Adı Ayarlama

1. Railway projenizin "Settings" sekmesinde "Networking" bölümünü bulun
2. "Generate Domain" seçeneğini tıklayın veya özel alan adı ekleyin
3. SSL sertifikası otomatik olarak oluşturulacaktır

### Daha Fazla Bilgi

Railway'in daha fazla özelliği ve yapılandırma seçenekleri için [Railway Dokümantasyonu](https://docs.railway.app) adresini ziyaret edin.
