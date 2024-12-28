import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import sqlite3
import hashlib
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules')))
from log_manager import LogWatcher

log_watcher = LogWatcher()

class AdminUserGUI:
    def __init__(self, root, username, cursor):  # Kullanıcı adını ekliyoruz
        self.root = root
        self.root.title("Sistem Yöneticisi Paneli")
        self.root.geometry("600x400")
        self.root.configure(bg='lightblue')

        # Log dosyalarının kaydedileceği dizin
        self.log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'modules', 'logs')

        # Veritabanı Bağlantısı
        self.cursor = cursor
        self.username = username  # Admin kullanıcı adı

        # Hoşgeldiniz mesajı
        self.lbl_welcome = tk.Label(self.root, text=f"Hoşgeldiniz, {username}!", bg='lightblue', font=('Arial', 14, 'bold'))
        self.lbl_welcome.pack(pady=20)

        # Yönetici arayüz bileşenlerini oluştur
        self.create_widgets()

    def create_widgets(self):
        # Kullanıcı yönetimi butonu
        btn_manage_users = tk.Button(self.root, text="Kullanıcı Yönetimi", command=self.manage_users, bg='yellow', fg='black')
        btn_manage_users.pack(pady=10)

        # Parola değiştirme onayı butonu
        btn_approve_password_change = tk.Button(self.root, text="Parola Değiştirme Onayı", command=self.approve_password_change, bg='orange', fg='black')
        btn_approve_password_change.pack(pady=10)

        # Depolama limitleri yönetimi butonu
        btn_manage_storage = tk.Button(self.root, text="Depolama Limitlerini Yönet", command=self.manage_storage, bg='blue', fg='white')
        btn_manage_storage.pack(pady=10)

        # Kullanıcı loglarını görüntüleme butonu
        btn_view_logs = tk.Button(self.root, text="Kullanıcı Loglarını Görüntüle", command=self.view_logs, bg='purple', fg='white')
        btn_view_logs.pack(pady=10)

        # Dosya erişim butonu
        btn_access_documents = tk.Button(self.root, text="Dokümanlara Erişim", command=self.access_documents, bg='red', fg='white')
        btn_access_documents.pack(pady=10)

        # Parola şifrelemesini gösterme butonu
        btn_view_passwords = tk.Button(self.root, text="Parolaları Görüntüle", command=self.view_passwords, bg='green', fg='white')
        btn_view_passwords.pack(pady=10)

        # Çıkış butonu
        tk.Button(self.root, text="Çıkış Yap", command=self.logout, bg='red', fg='white').pack(pady=10)

    def manage_users(self):
        # Kullanıcı profillerini listeleme penceresi
        manage_users_window = tk.Toplevel(self.root)
        manage_users_window.title("Kullanıcı Yönetimi")
        manage_users_window.geometry("600x400")
        manage_users_window.configure(bg='lightblue')

        tk.Label(manage_users_window, text="Kullanıcı Profilleri:", bg='lightblue', font=('Arial', 12)).pack(pady=10)
        listbox = tk.Listbox(manage_users_window, width=60, height=15)
        listbox.pack(pady=10)

        def refresh_list():
            """Listeyi yenilemek için kullanıcıları yeniden yükler."""
            listbox.delete(0, tk.END)  # Mevcut listeyi temizle
            self.cursor.execute("SELECT id, username, role FROM users")
            users = self.cursor.fetchall()
            for user in users:
                listbox.insert(tk.END, f"ID: {user[0]}, Username: {user[1]}, Role: {user[2]}")
            return users

        # İlk yükleme
        users = refresh_list()

        def change_role():
            # Seçili kullanıcı bilgilerini al
            selection = listbox.curselection()
            if selection:
                user_id = users[selection[0]][0]
                username = users[selection[0]][1]
                current_role = users[selection[0]][2]

                # Yeni rolü sor
                new_role = simpledialog.askstring("Rol Değiştir", f"{username} için yeni rolü girin (mevcut rol: {current_role}):")
                if new_role and new_role != current_role:
                    self.cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
                    self.cursor.connection.commit()
                    messagebox.showinfo("Başarılı", f"{username} kullanıcısının rolü '{new_role}' olarak güncellendi.")
                    refresh_list()  # Listeyi yenile
                else:
                    messagebox.showerror("Hata", "Geçersiz giriş veya aynı rol seçildi.")
            else:
                messagebox.showerror("Hata", "Lütfen bir kullanıcı seçin.")

        # Rol değiştirme butonu
        tk.Button(manage_users_window, text="Seçili Kullanıcının Rolünü Değiştir", command=change_role, bg='green', fg='white').pack(pady=10)

        # Yenile butonu
        tk.Button(manage_users_window, text="Yenile", command=refresh_list, bg='blue', fg='white').pack(pady=10)

    def approve_password_change(self):
        approval_window = tk.Toplevel(self.root)
        approval_window.title("Parola Değiştirme Talepleri")
        approval_window.geometry("600x400")
        approval_window.configure(bg='lightblue')

        # Talepleri getir
        self.cursor.execute("SELECT id, username FROM password_change_requests WHERE approved IS 0")
        requests = self.cursor.fetchall()

        if not requests:
            messagebox.showinfo("Bilgi", "Bekleyen bir parola değiştirme talebi yok.")
            return

        tk.Label(approval_window, text="Bekleyen Talepler:", bg='lightblue', font=('Arial', 12)).pack(pady=10)
        listbox = tk.Listbox(approval_window, width=50, height=10)
        listbox.pack(pady=10)

        for request in requests:
            listbox.insert(tk.END, f"ID: {request[0]}, Kullanıcı: {request[1]}")

        def approve_request():
            selection = listbox.curselection()
            if selection:
                request_id = requests[selection[0]][0]
                username = requests[selection[0]][1]

                # Onay işlemi
                self.cursor.execute("SELECT new_password FROM password_change_requests WHERE id = ?", (request_id,))
                new_hashed_password = self.cursor.fetchone()[0]

                self.cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_hashed_password, username))
                self.cursor.execute("UPDATE password_change_requests SET approved = 1 WHERE id = ?", (request_id,))
                self.cursor.connection.commit()

                messagebox.showinfo("Başarılı", f"{username} kullanıcısının yeni parolası onaylandı.")
                listbox.delete(selection[0])
                log_watcher.log_password_change_approval('PASSCHANGE001', 'SUCCESS', username)
            else:
                messagebox.showerror("Hata", "Lütfen bir talep seçin.")

        tk.Button(approval_window, text="Seçili Talebi Onayla", command=approve_request, bg='green', fg='white').pack(pady=10)

    def manage_storage(self):
        # Depolama limitlerini yönetme
        storage_window = tk.Toplevel(self.root)
        storage_window.title("Depolama Limiti Yönetimi")
        storage_window.geometry("600x400")
        storage_window.configure(bg='lightblue')

        tk.Label(storage_window, text="Depolama Limiti Yönetimi", bg='lightblue', font=('Arial', 14, 'bold')).pack(pady=20)

        self.cursor.execute("SELECT username, storage_limit FROM users")
        users = self.cursor.fetchall()

        # Kullanıcıları listeleme ve limitleri görüntüleme
        listbox = tk.Listbox(storage_window, width=50, height=10)
        listbox.pack(pady=10)

        for user in users:
            listbox.insert(tk.END, f"Username: {user[0]}, Depolama Limiti: {user[1]} GB")

        # Depolama limiti güncelleme butonu
        def update_storage_limit():
            selection = listbox.curselection()
            if selection:
                selected_user = users[selection[0]][0]
                new_limit = simpledialog.askinteger("Yeni Depolama Limiti", f"{selected_user} için yeni depolama limitini girin (GB):")
                
                if new_limit:
                    self.cursor.execute("UPDATE users SET storage_limit = ? WHERE username = ?", (new_limit, selected_user))
                    self.cursor.connection.commit()
                    messagebox.showinfo("Başarılı", f"{selected_user} için depolama limiti başarıyla güncellendi.")
                    listbox.delete(selection[0])
                    listbox.insert(tk.END, f"Username: {selected_user}, Depolama Limiti: {new_limit} GB")
                else:
                    messagebox.showerror("Hata", "Geçersiz giriş.")
            else:
                messagebox.showerror("Hata", "Lütfen bir kullanıcı seçin.")

        tk.Button(storage_window, text="Depolama Limiti Güncelle", command=update_storage_limit, bg='green', fg='white').pack(pady=10)

    def view_logs(self):
        try:
            # 'logs' dizinindeki tüm log dosyalarını al
            log_files = [f for f in os.listdir(self.log_dir) if f.endswith('.txt')]  # Sadece .txt dosyalarını al

            if log_files:
                # Log dosyalarının adlarını listele
                log_files_list = "\n".join(log_files)
                messagebox.showinfo("Log Dosyaları", f"Aşağıdaki log dosyalarını indirilebilir:\n{log_files_list}")
                
                # Kullanıcının bir log dosyasını seçmesini sağla
                selected_file = filedialog.askopenfilename(
                    initialdir=self.log_dir,
                    title="Log Dosyası Seçin",
                    filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
                )
                
                if selected_file:
                    # Seçilen dosyanın içeriğini oku
                    with open(selected_file, 'r') as file:
                        log_content = file.read()
                    
                    # Dosya içeriğini göster
                    messagebox.showinfo("Log Dosyası İçeriği", log_content)
            else:
                messagebox.showinfo("Kullanıcı Logları", "Hiçbir log kaydı bulunmamaktadır.")
        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu: {e}")

    def access_documents(self):
        # Kullanıcı dokümanlarına erişim
        document_window = tk.Toplevel(self.root)
        document_window.title("Kullanıcı Dokümanlarına Erişim")
        document_window.geometry("600x400")
        document_window.configure(bg='lightblue')

        # Kullanıcılara ait dokümanları file_shares tablosundan al
        self.cursor.execute("""
            SELECT file_name, file_path, shared_by, shared_with, share_date, team_name, editable 
            FROM file_shares
        """)
        documents = self.cursor.fetchall()

        # Listeleme alanı
        tk.Label(document_window, text="Kullanıcı Dokümanları:", bg='lightblue', font=('Arial', 12)).pack(pady=10)
        listbox = tk.Listbox(document_window, width=60, height=15)
        listbox.pack(pady=10)

        # Dokümanları listeye ekleyelim
        for document in documents:
            file_name, file_path, shared_by, shared_with, share_date, team_name, editable = document
            listbox.insert(tk.END, f"Dosya Adı: {file_name}, Takım: {team_name}, Paylaşan: {shared_by}, Paylaşılan: {shared_with}, Tarih: {share_date}, Düzenlenebilir: {editable}")

        # Dosyayı açma butonu
        def open_document():
            selection = listbox.curselection()
            if selection:
                selected_file = documents[selection[0]][1]  # Dosya yolunu al
                if os.path.exists(selected_file):
                    os.system(f"start {selected_file}")  # Dosyayı aç
                else:
                    messagebox.showerror("Hata", "Dosya bulunamadı.")
            else:
                messagebox.showerror("Hata", "Lütfen bir dosya seçin.")

        # Dosya açma butonu
        tk.Button(document_window, text="Dosyayı Aç", command=open_document, bg='green', fg='white').pack(pady=10)


    def view_passwords(self):
        # Parolaları şifreli olarak görüntüleme
        password_window = tk.Toplevel(self.root)
        password_window.title("Parolaları Görüntüle")
        password_window.geometry("600x400")
        password_window.configure(bg='lightblue')

        self.cursor.execute("SELECT username, password FROM users")
        users = self.cursor.fetchall()

        listbox = tk.Listbox(password_window, width=60, height=10)
        listbox.pack(pady=10)

        for user in users:
            listbox.insert(tk.END, f"Username: {user[0]}, Parola: {user[1]}")

        # Parolaları gizleme seçeneği
        def toggle_passwords():
            current_text = listbox.get(0, tk.END)
            listbox.delete(0, tk.END)
            for user in users:
                listbox.insert(tk.END, f"Username: {user[0]}, Parola: {user[1]}")

        tk.Button(password_window, text="Parolaları Gizle", command=toggle_passwords, bg='green', fg='white').pack(pady=10)

    def logout(self):
        # Çıkış yapma
        self.root.quit()

# Anlamlı ve kullanışlı admin pencereleriyle birlikte kullanıcıları etkili bir şekilde yönetebilirsiniz.
