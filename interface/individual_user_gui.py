import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import sqlite3
import hashlib

class IndividualUserGUI:
    def __init__(self, root, username, cursor, conn):
        self.root = root
        self.username = username
        self.cursor = cursor
        self.conn = conn  # Veritabanı bağlantısı
        self.root.title(f"{self.username} - Bireysel Kullanıcı Paneli")
        self.root.geometry("600x500")
        self.root.configure(bg='lightblue')
        self.lbl_welcome = tk.Label(self.root, text=f"Hoş Geldiniz, {self.username}!", bg='lightblue', font=('Arial', 16))
        self.lbl_welcome.pack(pady=10)
        self.status_label = tk.Label(self.root, text=" ", bg='lightblue', font=("Arial", 12))
        self.status_label.pack(pady=10)
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

        # Takım üyesi belirleme butonu
        btn_add_team_member = tk.Button(self.root, text="Takım Oluştur", command=self.create_team, bg='green', fg='white', width=30)
        btn_add_team_member.pack(pady=10)

        # Kullanıcının içinde olduğu takımları görüntüleme butonu
        btn_view_user_teams = tk.Button(self.root, text="Takımlarım", command=self.view_user_teams, bg='cyan', fg='black', width=30)
        btn_view_user_teams.pack(pady=10)

        # Dosya yükleme butonu
        btn_upload_file = tk.Button(self.root, text="Dosya Yükle", command=self.upload_file, bg='blue', fg='white', width=30)
        btn_upload_file.pack(pady=10)

        # Dosya paylaşma butonu
        btn_share_file = tk.Button(self.root, text="Dosya Paylaş", command=self.share_file, bg='purple', fg='white', width=30)
        btn_share_file.pack(pady=10)

    def change_username(self):
        new_username = simpledialog.askstring("Yeni Kullanıcı Adı", "Yeni kullanıcı adınızı girin:")
        if new_username:
            self.cursor.execute("UPDATE users SET username = ? WHERE username = ?", (new_username, self.username))
            self.cursor.connection.commit()
            self.username = new_username
            self.lbl_welcome.config(text=f"Hoş Geldiniz, {self.username}!")
            messagebox.showinfo("Başarılı", "Kullanıcı adı başarıyla değiştirildi!")
        else:
            messagebox.showerror("Hata", "Geçersiz kullanıcı adı.")
            
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
        self.cursor.execute("SELECT approved FROM password_change_requests WHERE username = ?", (self.username,))
        result = self.cursor.fetchone()
        if result is None:
            self.status_label.config(text="Herhangi bir talebiniz bulunmamaktadır.", fg='blue')
        elif result[0] is None:
            self.status_label.config(text="Talebiniz onay bekliyor.", fg='orange')
        elif result[0] == 1:
            self.status_label.config(text="Talebiniz onaylanmıştır.", fg='green')
        elif result[0] == 0:
            self.status_label.config(text="Talebiniz reddedilmiştir.", fg='red')
        else:
            self.status_label.config(text="Bilinmeyen bir durum oluştu.", fg='gray')


    def upload_file(self):
        file = filedialog.askopenfilename(title="Bir dosya seçin")
        if file:
            messagebox.showinfo("Dosya Yüklendi", f"{file} başarıyla yüklendi!")


    def send_notification(self, username, message):
        messagebox.showinfo("Bildirim", f"{username}: {message}")

    def create_team(self):
        team_name = simpledialog.askstring("Takım Oluştur", "Takım adını girin:")
        if not team_name:
            return
        
        # Takım oluşturuluyor
        self.cursor.execute("INSERT INTO teams (owner_username, team_name) VALUES (?, ?)", 
                            (self.username, team_name))
        self.conn.commit()

        users_window = tk.Toplevel(self.root)
        users_window.title("Takım Üyesi Seç")

        tk.Label(users_window, text="Takımınıza eklemek için bir kullanıcı seçin:").pack(pady=5)

        # Kullanıcıları listeleyen Listbox
        users_listbox = tk.Listbox(users_window, selectmode=tk.SINGLE)  # Tekli seçim için SINGLE kullanılır
        users_listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        # Kullanıcıları veritabanından al
        self.cursor.execute("SELECT username FROM users WHERE username != ?", (self.username,))
        users = self.cursor.fetchall()

        for user in users:
            users_listbox.insert(tk.END, user[0])

        # Ekle butonu
        def add_selected_member():
            selected_member = users_listbox.get(users_listbox.curselection())  # Seçilen kullanıcı
            if selected_member:
                # Kullanıcının zaten bu takımda olup olmadığını kontrol et
                self.cursor.execute("SELECT 1 FROM team_members WHERE team_name = ? AND member_username = ?", (team_name, selected_member))
                if self.cursor.fetchone():
                    messagebox.showerror("Hata", f"{selected_member} zaten bu takımda yer alıyor!")
                    return
                
                try:
                    # Veritabanına ekle
                    self.cursor.execute("INSERT INTO team_members (team_name, member_username, owner_username) VALUES (?, ?, ?)",
                                        (team_name, selected_member, self.username))
                    self.conn.commit()
                    messagebox.showinfo("Başarılı", f"{selected_member} başarıyla eklendi.")
                except sqlite3.Error as e:
                    messagebox.showerror("Hata", f"Üye eklenirken bir hata oluştu: {e}")
            else:
                messagebox.showerror("Hata", "Bir kullanıcı seçmelisiniz.")

        # Ekle butonu
        btn_add_member = tk.Button(users_window, text="Ekle", command=add_selected_member, bg='green', fg='white')
        btn_add_member.pack(pady=10)

        # Pencereyi kapatma butonu
        btn_close_window = tk.Button(users_window, text="Kapat", command=users_window.destroy, bg='red', fg='white')
        btn_close_window.pack(pady=5)


    def view_user_teams(self):
        # Kullanıcının yer aldığı ve sahip olduğu takımları sorgula
        self.cursor.execute("""
            SELECT DISTINCT team_name
            FROM team_members
            WHERE member_username = ? OR owner_username = ?
        """, (self.username, self.username))
        teams = self.cursor.fetchall()

        if not teams:
            messagebox.showinfo("Bilgi", "Bu kullanıcıya ait herhangi bir takım bulunmamaktadır.")
            return

        # Takımları görüntülemek için yeni pencere oluştur
        teams_window = tk.Toplevel(self.root)
        teams_window.title(f"{self.username} - Takımlarım")

        # Kullanıcıya takımlarını gösterecek olan başlık
        tk.Label(teams_window, text=f"{self.username} - Katıldığınız Takımlar:", font=("Arial", 14)).pack(pady=10)

        # Listbox widget'ı oluştur
        teams_listbox = tk.Listbox(teams_window, selectmode=tk.SINGLE)
        teams_listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Takımları Listbox'a ekle
        for team in teams:
            teams_listbox.insert(tk.END, team[0])

        # Takımın sahibi olup olmadığını kontrol et
        def check_owner_permission(team_name):
            self.cursor.execute("SELECT owner_username FROM teams WHERE team_name = ?", (team_name,))
            owner = self.cursor.fetchone()
            if owner and owner[0] == self.username:  # Eğer kullanıcı takımın sahibi ise
                return True
            return False

        # Takım üyelerini görüntüle butonu
        btn_view_team_members = tk.Button(teams_window, text="Takım Üyelerini Görüntüle", command=lambda: self.view_team_members(teams_listbox.get(tk.ACTIVE)), bg='green', fg='white')
        btn_view_team_members.pack(pady=10)

        # Takım üyesi ekleme butonu (Sadece takım sahibi görmeli)
        def add_member_button_click():
            selected_team = teams_listbox.get(tk.ACTIVE)
            if check_owner_permission(selected_team):
                self.add_member_to_team(selected_team)
            else:
                messagebox.showerror("Yetki Hatası", "Bu takımın sahibi değilsiniz.")

        btn_add_member = tk.Button(teams_window, text="Takım Üyesi Ekle", command=add_member_button_click, bg='blue', fg='white')
        btn_add_member.pack(pady=10)

    def add_member_to_team(self, team_name):
        users_window = tk.Toplevel(self.root)
        users_window.title(f"{team_name} - Üye Ekle")

        tk.Label(users_window, text="Takımınıza eklemek için bir kullanıcı seçin:").pack(pady=5)

        # Kullanıcıları listeleyen Listbox
        users_listbox = tk.Listbox(users_window, selectmode=tk.SINGLE)  # Tekli seçim için SINGLE kullanılır
        users_listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        # Kullanıcıları veritabanından al
        self.cursor.execute("SELECT username FROM users WHERE username != ?", (self.username,))
        users = self.cursor.fetchall()

        for user in users:
            users_listbox.insert(tk.END, user[0])

        # Ekle butonu
        def add_selected_member():
            selected_member = users_listbox.get(users_listbox.curselection())  # Seçilen kullanıcı
            if selected_member:
                # Kullanıcının zaten bu takımda olup olmadığını kontrol et
                self.cursor.execute("SELECT 1 FROM team_members WHERE team_name = ? AND member_username = ?", (team_name, selected_member))
                if self.cursor.fetchone():
                    messagebox.showerror("Hata", f"{selected_member} zaten bu takımda yer alıyor!")
                    return
                
                try:
                    # Veritabanına ekle
                    self.cursor.execute("INSERT INTO team_members (team_name, member_username, owner_username) VALUES (?, ?, ?)",
                                        (team_name, selected_member, self.username))
                    self.conn.commit()
                    messagebox.showinfo("Başarılı", f"{selected_member} başarıyla eklendi.")
                except sqlite3.Error as e:
                    messagebox.showerror("Hata", f"Üye eklenirken bir hata oluştu: {e}")
            else:
                messagebox.showerror("Hata", "Bir kullanıcı seçmelisiniz.")

        # Ekle butonu
        btn_add_member = tk.Button(users_window, text="Ekle", command=add_selected_member, bg='green', fg='white')
        btn_add_member.pack(pady=10)

        # Pencereyi kapatma butonu
        btn_close_window = tk.Button(users_window, text="Kapat", command=users_window.destroy, bg='red', fg='white')
        btn_close_window.pack(pady=5)




    def view_team_members(self, team_name):
        if not team_name:
            messagebox.showerror("Hata", "Bir takım seçmelisiniz.")
            return

        # Seçilen takımın üyelerini veritabanından sorgula
        self.cursor.execute("SELECT member_username FROM team_members WHERE team_name = ?", (team_name,))
        members = self.cursor.fetchall()

        if not members:
            messagebox.showinfo("Bilgi", f"{team_name} takımında üye bulunmamaktadır.")
            return

        # Takım üyelerini görüntülemek için yeni pencere oluştur
        members_window = tk.Toplevel(self.root)
        members_window.title(f"{team_name} Takımı Üyeleri")

        # Üyeleri listeleyecek olan başlık
        tk.Label(members_window, text=f"{team_name} Takımı Üyeleri:", font=("Arial", 14)).pack(pady=10)

        # Listbox widget'ı oluştur
        members_listbox = tk.Listbox(members_window)
        members_listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Üyeleri Listbox'a ekle
        for member in members:
            members_listbox.insert(tk.END, member[0])




    def share_file(self):
        team_name = simpledialog.askstring("Dosya Paylaş", "Dosyayı paylaşmak istediğiniz takım adını girin:")
        if not team_name:
            return
        
        self.cursor.execute("SELECT member_username FROM team_members WHERE team_name = ?", (team_name,))
        members = self.cursor.fetchall()
        
        if not members:
            messagebox.showerror("Hata", f"{team_name} takımına ait üye bulunamadı.")
            return

        file_path = filedialog.askopenfilename(title="Bir dosya seçin")
        if file_path:
            # Dosya paylaşım işlemleri (gerçekleştirilecek işlemler eklenebilir)
            member_list = ", ".join([member[0] for member in members])
            messagebox.showinfo("Başarılı", f"{team_name} takımına ({member_list}) {file_path} başarıyla paylaşıldı!")

    def logout(self):
        self.root.destroy()

    def __del__(self):
        self.conn.close()