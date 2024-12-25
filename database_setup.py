import sqlite3

# Veritabanı bağlantısını kur
conn = sqlite3.connect('file_backup_system.db')
cursor = conn.cursor()

cursor.execute("ALTER TABLE team_members ADD COLUMN team_name TEXT;")



# Değişiklikleri kaydet ve bağlantıyı kapat
conn.commit()
conn.close()

print("Tablo başarıyla oluşturuldu!")
