import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
import sys
import os
from individual_user_gui import IndividualUserGUI
from admin_user_gui import AdminUserGUI
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules')))
from backup_sync import FileBackupApp
from log_manager import LogWatcher  # modules/log_manager.py
from behavior_analyzer import UserBehaviorWatcher  # modules/behavior_analyzer.py
from log_manager import LogWatcher

log_watcher = LogWatcher()

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dosya Depolama/Yedekleme Sistemi")
        self.root.geometry("600x400")
        self.root.configure(bg='lightpink')  # Arka plan rengi 

        self.failed_attempts = 0  # Başarısız giriş sayısı

        # Veritabanı Bağlantısı
        self.conn = sqlite3.connect('file_backup_system.db')
        self.cursor = self.conn.cursor()

        # Giriş Ekranı
        self.create_login_screen()

        # Yedekleme ve Senkronizasyonu başlatıyoruz
        self.start_backup_sync()

        # Log İzleme ve Davranış İzleme başlatıyoruz
        self.start_log_and_behavior_monitoring()

    def start_backup_sync(self):
        """Yedekleme ve senkronizasyon işlemini başlatır."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        source_dir = os.path.join(project_root, "modules/source")
        backup_dir = os.path.join(project_root, "modules/backup")

        # Yedekleme işlemi başlatılıyor
        file_sync = FileBackupApp(self.root, source_dir, backup_dir)
        
        # Yedekleme işlemi için log kaydediliyor
        log_watcher = LogWatcher()
        log_watcher.log_backup('BACKUP001', 'SUCCESS', source_dir, 150)  # Yedekleme başarılı oldu (150MB)

        # Kullanıcıya bildirim mesajı
        messagebox.showinfo("Yedekleme Tamamlandı", "Yedekleme işlemi başarıyla tamamlandı!")

    def start_log_and_behavior_monitoring(self):
        """Log İzleme ve Kullanıcı Davranışı İzlemeyi başlatır."""
        # Log İzleyicisini başlat
        log_watcher = LogWatcher()
        log_watcher.log('log_start', 'INFO', 'START', 'N/A', 0)  # Log başlatılıyor
        log_watcher.start()

        # Kullanıcı Davranışı İzleyicisini başlat
        behavior_watcher = UserBehaviorWatcher(log_watcher, self.show_alert)
        behavior_watcher.start()

    def show_alert(self, message):
        """Tkinter GUI üzerinde uyarı göstermek için fonksiyon."""
        alert_window = tk.Toplevel(self.root)
        alert_window.title("Uyarı")
        label = tk.Label(alert_window, text=message)
        label.pack(padx=20, pady=20)
        button = tk.Button(alert_window, text="Tamam", command=alert_window.destroy)
        button.pack(pady=10)

    def create_login_screen(self):
        """Kullanıcı girişi için ekranı oluşturur."""
        # Kullanıcı Adı
        tk.Label(self.root, text="Kullanıcı Adı:", bg='lightpink', font=('Arial', 12)).pack(pady=5)
        self.entry_username = tk.Entry(self.root, bg='white', fg='black')
        self.entry_username.pack(pady=5)

        # Parola
        tk.Label(self.root, text="Parola:", bg='lightpink', font=('Arial', 12)).pack(pady=5)
        self.entry_password = tk.Entry(self.root, show="*", bg='white', fg='black')
        self.entry_password.pack(pady=5)

        # Giriş Yap Butonu
        tk.Button(self.root, text="Giriş Yap", command=self.login, bg='gray', fg='white').pack(pady=10)

        # Kayıt Ol Butonu
        tk.Button(self.root, text="Kayıt Ol", command=self.register, bg='gray', fg='white').pack(pady=10)

        # Çıkış Yap Butonu (Uygulamayı kapatır)
        tk.Button(self.root, text="Çıkış Yap", command=self.exit_application, bg='red', fg='white').pack(pady=10)

    def hash_password(self, password):
        """Parolayı SHA256 ile hashler."""
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self):
        """Kullanıcı giriş işlemi."""
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not username or not password:
            messagebox.showerror("Hata", "Kullanıcı adı ve parola boş bırakılamaz.")
            return

        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = self.cursor.fetchone()

        if user and self.hash_password(password) == user[2]:  # user[2] = stored password hash
            messagebox.showinfo("Başarılı", "Giriş Başarılı!")

            # Profil girişi başarılı olduğunda log kaydını yapıyoruz
            log_watcher = LogWatcher()  # LogWatcher sınıfından bir nesne oluşturuyoruz
            log_watcher.log_profile_login(username)  # Profil girişini logluyoruz
            
            if user[3] == "admin":  # user[3] = role
                self.admin_dashboard(username)
            else:
                self.user_dashboard(username)
            self.root.withdraw()  # Giriş penceresini gizle

        else:
            # Başarısız giriş işlemi
            self.failed_attempts += 1
            if self.failed_attempts >= 3:  # 3 başarısız giriş tespiti
                self.detect_anomaly(username)

            messagebox.showerror("Hata", "Kullanıcı adı veya parola yanlış.")

    def detect_anomaly(self, username):
        """Kullanıcının davranışını izler ve anormal bir durum tespit ederse log kaydeder."""
        log_watcher = LogWatcher()
        log_watcher.log_anomaly('ANOMALY001', 'ALERT', username, 'Three failed login attempts in a short period.')

        # Kullanıcıya bildirim
        messagebox.showwarning("Anomali Tespit Edildi", f"Anormal durum tespit edildi: {username}.")


    def register(self):
        """Kayıt ekranını açar."""
        register_window = tk.Toplevel(self.root)
        register_window.title("Kayıt Ol")
        register_window.geometry("400x300")
        register_window.configure(bg='lightblue')

        # Kullanıcı Adı
        tk.Label(register_window, text="Kullanıcı Adı:", bg='lightblue', font=('Arial', 12)).pack(pady=5)
        entry_username = tk.Entry(register_window, bg='white', fg='black')
        entry_username.pack(pady=5)

        # Parola
        tk.Label(register_window, text="Parola:", bg='lightblue', font=('Arial', 12)).pack(pady=5)
        entry_password = tk.Entry(register_window, show="*", bg='white', fg='black')
        entry_password.pack(pady=5)

        # Parola Onay
        tk.Label(register_window, text="Parolayı Onayla:", bg='lightblue', font=('Arial', 12)).pack(pady=5)
        entry_password_confirm = tk.Entry(register_window, show="*", bg='white', fg='black')
        entry_password_confirm.pack(pady=5)

        # Kayıt Ol Butonu
        tk.Button(
            register_window,
            text="Kayıt Ol",
            command=lambda: self.create_account(
                entry_username.get().strip(),
                entry_password.get().strip(),
                entry_password_confirm.get().strip(),
                register_window
            ),
            bg='green',
            fg='white'
        ).pack(pady=10)

    def create_account(self, username, password, password_confirm, window):
        """Yeni kullanıcı kaydı oluşturur."""
        if not username or not password:
            messagebox.showerror("Hata", "Kullanıcı adı ve parola boş bırakılamaz.")
            return

        if password != password_confirm:
            messagebox.showerror("Hata", "Parolalar uyuşmuyor.")
            return

        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if self.cursor.fetchone():
            messagebox.showerror("Hata", "Bu kullanıcı adı zaten alınmış.")
            return

        hashed_password = self.hash_password(password)
        self.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_password, 'individual'))
        self.conn.commit()

        messagebox.showinfo("Başarılı", "Kayıt başarılı!")
        window.destroy()

    def user_dashboard(self, username):
        user_window = tk.Toplevel(self.root)
        conn = sqlite3.connect("file_backup_system.db")  # Veritabanı bağlantısı burada oluşturuluyor
        cursor = conn.cursor()  # Cursor da burada oluşturuluyor
        IndividualUserGUI(user_window, username, cursor, conn)  # Veritabanı bağlantısını ve cursor'u geçiriyoruz

    def admin_dashboard(self, username):
        """Yönetici panelini açar."""
        admin_window = tk.Toplevel(self.root)
        admin_window.title("Yönetici Paneli")
        admin_window.geometry("600x500")
        admin_window.configure(bg='lightblue')

        AdminUserGUI(admin_window, username, self.cursor)

    def exit_application(self):
        """Uygulamayı kapatır."""
        if messagebox.askyesno("Çıkış", "Uygulamadan çıkmak istiyor musunuz?"):
            self.conn.close()
            self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
