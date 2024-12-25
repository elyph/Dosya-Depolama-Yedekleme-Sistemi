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
        self.root.configure(bg='lightblue')  # Arka plan rengini değiştirdik

        # Veritabanı Bağlantısı
        self.conn = sqlite3.connect('file_backup_system.db')
        self.cursor = self.conn.cursor()

        # Kullanıcı Girişi
        self.lbl_username = tk.Label(root, text="Kullanıcı Adı:", bg='lightblue', font=('Arial', 12))
        self.lbl_username.pack(pady=5)
        self.entry_username = tk.Entry(root, bg='white', fg='black')
        self.entry_username.pack(pady=5)

        self.lbl_password = tk.Label(root, text="Parola:", bg='lightblue', font=('Arial', 12))
        self.lbl_password.pack(pady=5)
        self.entry_password = tk.Entry(root, show="*", bg='white', fg='black')
        self.entry_password.pack(pady=5)

        self.btn_login = tk.Button(root, text="Giriş Yap", command=self.login, bg='blue', fg='white')
        self.btn_login.pack(pady=10)

        self.btn_register = tk.Button(root, text="Kayıt Ol", command=self.register, bg='green', fg='white')
        self.btn_register.pack(pady=10)

    def hash_password(self, password):
        # SHA256 ile parolayı hash'le
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, stored_hash, input_password):
        # Kullanıcının girdiği parolayı hash'le ve veritabanındaki hash ile karşılaştır
        return stored_hash == self.hash_password(input_password)

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        # Kullanıcıyı veritabanından kontrol et
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = self.cursor.fetchone()

        if user:
            # Parola doğrulaması yap
            stored_hash = user[2]  # user[2] = password column
            if self.hash_password(password) == stored_hash:
                messagebox.showinfo("Başarılı", "Giriş Başarılı!")
                if user[3] == "admin":  # admin rolü
                    self.admin_dashboard(username)  # Burada username'i admin_dashboard fonksiyonuna gönderiyoruz
                else:
                    self.user_dashboard(username)
            else:
                messagebox.showerror("Hata", "Parola hatalı.")
        else:
            messagebox.showerror("Hata", "Kullanıcı adı bulunamadı.")

    def register(self):
        self.new_window = tk.Toplevel(self.root)
        self.new_window.title("Kayıt Ol")
        self.new_window.geometry("400x300")
        self.new_window.configure(bg='lightblue')

        # Kayıt Ekranı
        lbl_username = tk.Label(self.new_window, text="Kullanıcı Adı:", bg='lightblue', font=('Arial', 12))
        lbl_username.pack(pady=5)
        entry_username = tk.Entry(self.new_window, bg='white', fg='black')
        entry_username.pack(pady=5)

        lbl_password = tk.Label(self.new_window, text="Parola:", bg='lightblue', font=('Arial', 12))
        lbl_password.pack(pady=5)
        entry_password = tk.Entry(self.new_window, show="*", bg='white', fg='black')
        entry_password.pack(pady=5)

        lbl_password_confirm = tk.Label(self.new_window, text="Parolayı Onayla:", bg='lightblue', font=('Arial', 12))
        lbl_password_confirm.pack(pady=5)
        entry_password_confirm = tk.Entry(self.new_window, show="*", bg='white', fg='black')
        entry_password_confirm.pack(pady=5)

        btn_register = tk.Button(self.new_window, text="Kayıt Ol", 
                                  command=lambda: self.create_account(entry_username.get(), entry_password.get(), entry_password_confirm.get()), 
                                  bg='green', fg='white')
        btn_register.pack(pady=10)

    def create_account(self, username, password, password_confirm):
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = self.cursor.fetchone()

        if user:
            messagebox.showerror("Hata", "Bu kullanıcı adı zaten alınmış.")
        elif password != password_confirm:
            messagebox.showerror("Hata", "Parolalar uyuşmuyor.")
        else:
            hashed_password = self.hash_password(password)
            # Varsayılan olarak bireysel kullanıcı (individual) olarak kaydediyoruz
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_password, 'individual'))
            self.conn.commit()
            messagebox.showinfo("Başarılı", "Kayıt başarılı!")
            self.new_window.destroy()

    def user_dashboard(self, username):
        # Bireysel kullanıcı paneline yönlendir
        self.new_window = tk.Toplevel(self.root)
        self.new_window.title(f"{username} Bireysel Kullanıcı Paneli")
        self.new_window.geometry("600x400")
        self.new_window.configure(bg='lightblue')

        # Bireysel Kullanıcı Paneli için GUI'yi başlat
        individual_user_gui = IndividualUserGUI(self.new_window, username, self.cursor)

        # Burada, Bireysel Kullanıcı Arayüzüne dair diğer bileşenler de yüklenmiş olacak.


    def admin_dashboard(self, username):
        # Admin Paneli için yeni pencere açma ve kullanıcı adı gönderme
        self.new_window = tk.Toplevel(self.root)
        self.new_window.title("Yönetici Paneli")
        self.new_window.geometry("600x400")
        self.new_window.configure(bg='lightblue')

        # Burada username'i AdminUserGUI'ye parametre olarak geçiriyoruz
        admin_user_gui = AdminUserGUI(self.new_window, username, self.cursor)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
