import sqlite3

# Veritabanı bağlantısını kur
conn = sqlite3.connect('file_backup_system.db')
cursor = conn.cursor()

# Eski tabloyu kaldır
cursor.execute("DROP TABLE IF EXISTS password_change_requests")

# Yeni tabloyu oluştur
cursor.execute('''
CREATE TABLE password_change_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    new_password TEXT NOT NULL,
    approved INTEGER DEFAULT 0
);
''')

# Değişiklikleri kaydet ve bağlantıyı kapat
conn.commit()
conn.close()

print("Tablo başarıyla yeniden oluşturuldu!")