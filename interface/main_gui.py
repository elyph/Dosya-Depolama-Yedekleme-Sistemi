import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
from individual_user_gui import IndividualUserGUI
from admin_user_gui import AdminUserGUI

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dosya Depolama/Yedekleme Sistemi")
        self.root.geometry("600x400")
        self.root.configure(bg='lightblue')  # Arka plan rengi

        # Veritabanı Bağlantısı
        self.conn = sqlite3.connect('file_backup_system.db')
        self.cursor = self.conn.cursor()

        # Giriş Ekranı
        self.create_login_screen()

    def create_login_screen(self):
        """Kullanıcı girişi için ekranı oluşturur."""
        # Kullanıcı Adı
        tk.Label(self.root, text="Kullanıcı Adı:", bg='lightblue', font=('Arial', 12)).pack(pady=5)
        self.entry_username = tk.Entry(self.root, bg='white', fg='black')
        self.entry_username.pack(pady=5)

        # Parola
        tk.Label(self.root, text="Parola:", bg='lightblue', font=('Arial', 12)).pack(pady=5)
        self.entry_password = tk.Entry(self.root, show="*", bg='white', fg='black')
        self.entry_password.pack(pady=5)

        # Giriş Yap Butonu
        tk.Button(self.root, text="Giriş Yap", command=self.login, bg='blue', fg='white').pack(pady=10)

        # Kayıt Ol Butonu
        tk.Button(self.root, text="Kayıt Ol", command=self.register, bg='green', fg='white').pack(pady=10)

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
            if user[3] == "admin":  # user[3] = role
                self.admin_dashboard(username)
            else:
                self.user_dashboard(username)
        else:
            messagebox.showerror("Hata", "Geçersiz kullanıcı adı veya parola.")

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

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
