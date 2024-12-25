import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import sqlite3
import hashlib

class IndividualUserGUI:
    def __init__(self, root, username, cursor):
        self.root = root
        self.username = username
        self.cursor = cursor
        self.root.title(f"{self.username} - Bireysel Kullanıcı Paneli")
        self.root.geometry("600x500")
        self.root.configure(bg='lightblue')

        # Hoş Geldiniz etiketini sınıf değişkeni olarak tanımladık
        self.lbl_welcome = tk.Label(self.root, text=f"Hoş Geldiniz, {self.username}!", bg='lightblue', font=('Arial', 16))
        self.lbl_welcome.pack(pady=10)

        self.status_label = tk.Label(self.root, text=" ", bg='lightblue', font=("Arial", 12)) #Talep durumu
        self.status_label.pack(pady=10)

        # Kullanıcı arayüz bileşenlerini buraya ekleyebilirsiniz
        self.create_widgets()

    def create_widgets(self):
        # Kullanıcı adı değiştirme butonu
        btn_change_username = tk.Button(self.root, text="Kullanıcı Adı Değiştir", command=self.change_username, bg='yellow', fg='black', width=30)
        btn_change_username.pack(pady=10)

        # Parola değiştirme talebi gönderme butonu
        btn_request_password_change = tk.Button(self.root, text="Parola Değiştirme Talebi", command=self.request_password_change, bg='orange', fg='black', width=30)
        btn_request_password_change.pack(pady=10)

        # Parola değişikliği kontrol etme butonu
        btn_check_status = tk.Button(self.root, text="Parola Değişikliği Durumu", command=self.check_request_status, bg='orange', fg='black', width=30)
        btn_check_status.pack(pady=10)

        # Dosya yükleme butonu
        btn_upload_file = tk.Button(self.root, text="Dosya Yükle", command=self.upload_file, bg='blue', fg='white', width=30)
        btn_upload_file.pack(pady=10)

        # Takım üyesi belirleme butonu
        btn_add_team_member = tk.Button(self.root, text="Takım Üyesi Ekle", command=self.add_team_member, bg='green', fg='white', width=30)
        btn_add_team_member.pack(pady=10)

        # Dosya paylaşma butonu
        btn_share_file = tk.Button(self.root, text="Dosya Paylaş", command=self.share_file, bg='purple', fg='white', width=30)
        btn_share_file.pack(pady=10)

    def change_username(self):
        new_username = simpledialog.askstring("Yeni Kullanıcı Adı", "Yeni kullanıcı adınızı girin:")
        if new_username:
            # Kullanıcı adı değiştirme işlemi
            self.cursor.execute("UPDATE users SET username = ? WHERE username = ?", (new_username, self.username))
            self.cursor.connection.commit()
            self.username = new_username  # Güncellenen kullanıcı adını tut
            messagebox.showinfo("Başarılı", "Kullanıcı adı başarıyla değiştirildi!")
            
            # Hoş Geldiniz mesajını güncelle
            self.lbl_welcome.config(text=f"Hoş Geldiniz, {self.username}!")  # Hoşgeldiniz mesajını güncelle

    def request_password_change(self):
        new_password = simpledialog.askstring("Yeni Parola", "Yeni parolanızı girin:")
        
        if new_password:
            hashed_password = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
            self.cursor.execute(
                "INSERT INTO password_change_requests (username, new_password) VALUES (?, ?)",
                (self.username, hashed_password)
            )
            self.cursor.connection.commit()
            messagebox.showinfo("Talep Gönderildi", "Parola değişikliği talebiniz sistem yöneticisine gönderildi.")
            self.status_label.config(text="Parola değişikliği talebiniz gönderildi.", fg='green')
        else:
            messagebox.showerror("Hata", "Parola boş olamaz!")



    def check_request_status(self):
        self.cursor.execute(
            "SELECT approved FROM password_change_requests WHERE username = ?", 
            (self.username,)
        )
        result = self.cursor.fetchone()

        if result is None:  # Kullanıcının talebi yok
            self.status_label.config(text="Herhangi bir talebiniz bulunmamaktadır.", fg='blue')
        elif result[0] is None:  # Talep var ama henüz onaylanmamış
            self.status_label.config(text="Talebiniz onay bekliyor.", fg='orange')
        elif result[0] == 1:  # Talep onaylanmış
            self.status_label.config(text="Talebiniz onaylanmıştır.", fg='green')
        elif result[0] == 0:  # Talep reddedilmiş
            self.status_label.config(text="Talebiniz reddedilmiştir.", fg='red')
        else:
            self.status_label.config(text="Bilinmeyen bir durum oluştu.", fg='gray')




    def upload_file(self):
        file = filedialog.askopenfilename(title="Bir dosya seçin")
        if file:
            messagebox.showinfo("Dosya Yüklendi", f"{file} başarıyla yüklendi!")

    def add_team_member(self):
        team_member = simpledialog.askstring("Takım Üyesi Ekle", "Takım üyesinin kullanıcı adını girin:")
        if team_member:
            self.cursor.execute("SELECT * FROM users WHERE username = ?", (team_member,))
            user = self.cursor.fetchone()
            if user:
                self.cursor.execute("INSERT INTO team_members (username, team_member) VALUES (?, ?)", (self.username, team_member))
                self.cursor.connection.commit()
                messagebox.showinfo("Başarılı", f"{team_member} başarıyla takım üyesi olarak eklendi!")
                self.send_notification(team_member, "Yeni bir takım üyesi olarak eklendiniz!")
            else:
                messagebox.showerror("Hata", "Kullanıcı adı bulunamadı.")

    def send_notification(self, username, message):
        messagebox.showinfo("Bildirim", f"{username}: {message}")

    def share_file(self):
        team_member = simpledialog.askstring("Dosya Paylaş", "Dosyayı paylaşmak istediğiniz kullanıcı adını girin:")
        if team_member:
            self.cursor.execute("SELECT * FROM team_members WHERE username = ? AND team_member = ?", (self.username, team_member))
            if self.cursor.fetchone():
                file = filedialog.askopenfilename(title="Bir dosya seçin")
                if file:
                    messagebox.showinfo("Başarılı", f"{team_member} ile {file} dosyası başarıyla paylaşıldı!")
            else:
                messagebox.showerror("Hata", "Bu kullanıcıyla takım üyesi değilsiniz.")
