import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import hashlib

class AdminUserGUI:
    def __init__(self, root, username, cursor):  # Kullanıcı adını ekliyoruz
        self.root = root
        self.root.title("Sistem Yöneticisi Paneli")
        self.root.geometry("600x400")
        self.root.configure(bg='lightblue')

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

        #Çıkış butonu
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
        self.cursor.execute("SELECT id, username FROM password_change_requests WHERE approved IS NULL")
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
                    messagebox.showinfo("Başarılı", f"{selected_user} için depolama limiti başarıyla {new_limit} GB olarak güncellendi.")
                else:
                    messagebox.showerror("Hata", "Geçersiz giriş.")
            else:
                messagebox.showerror("Hata", "Lütfen bir kullanıcı seçin.")

        tk.Button(storage_window, text="Seçili Kullanıcıyı Güncelle", command=update_storage_limit, bg='green', fg='white').pack(pady=10)

    def view_logs(self):
        # Kullanıcı loglarını görüntüleme
        self.cursor.execute("SELECT * FROM logs")
        logs = self.cursor.fetchall()
        logs_list = "\n".join([f"Log ID: {log[0]}, Username: {log[1]}, Action: {log[2]}, Date: {log[3]}" for log in logs])

        messagebox.showinfo("Kullanıcı Logları", f"Kullanıcı Logları:\n{logs_list}")

    def access_documents(self):
        # Dokümanlara erişim
        username = simpledialog.askstring("Doküman Erişimi", "Erişmek istediğiniz kullanıcının kullanıcı adını girin:")
        
        self.cursor.execute("SELECT * FROM documents WHERE username = ?", (username,))
        documents = self.cursor.fetchall()
        
        if documents:
            docs_list = "\n".join([f"Document: {doc[1]}, Type: {doc[2]}" for doc in documents])
            messagebox.showinfo("Dokümanlar", f"{username} kullanıcısının dokümanları:\n{docs_list}")
        else:
            messagebox.showerror("Hata", f"{username} kullanıcısının dokümanı bulunamadı.")

    def logout(self):
        """Kullanıcı çıkış yaparsa, giriş ekranına döner."""
        if messagebox.askyesno("Çıkış", "Çıkış yapmak istediğinizden emin misiniz?"):
            self.root.destroy()  # Kullanıcı panelini kapat
            self.return_to_main_screen()  # Giriş ekranına dön

    def return_to_main_screen(self):
        """Ana ekranı (giriş ekranı) yeniden başlatır."""
        from main_gui import MainApp  # Ana ekran sınıfını içe aktar
        main_root = tk.Tk()
        app = MainApp(main_root)
        main_root.mainloop()