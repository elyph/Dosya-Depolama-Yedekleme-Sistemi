import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime

class NotificationManager:
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.cursor = db_connection.cursor()

    def add_notification(self, message, username):
        self.cursor.execute(
            "INSERT INTO notifications (username, message, timestamp, is_read) VALUES (?, ?, datetime('now'), 0)",
            (username, message),
        )
        self.db_connection.commit()  # 'conn' yerine 'self.db_connection' kullanıldı

    def get_notifications(self, username):
        self.cursor.execute(
            "SELECT id, message, timestamp, is_read FROM notifications WHERE username = ?",
            (username,),
        )
        return [
            {"id": row[0], "message": row[1], "timestamp": row[2], "is_read": row[3]}
            for row in self.cursor.fetchall()
        ]

    def mark_as_read(self, notification_id):
        self.cursor.execute(
            "UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,)
        )
        self.db_connection.commit()  # 'conn' yerine 'self.db_connection' kullanıldı

    def remove_notification(self, notification_id):
        self.cursor.execute("DELETE FROM notifications WHERE id = ?", (notification_id,))
        self.db_connection.commit()  # 'conn' yerine 'self.db_connection' kullanıldı

class UserNotificationsApp:
    def __init__(self, root, notification_manager, username):
        self.root = root
        self.root.title("Bildirimler")
        self.notification_manager = notification_manager
        self.username = username
        self.create_widgets()

    def create_widgets(self):
        self.frame = ttk.Frame(self.root)
        self.frame.pack(padx=20, pady=20)

        self.title_label = ttk.Label(self.frame, text="Bildirimler", font=("Arial", 16))
        self.title_label.grid(row=0, column=0, pady=10)

        self.notification_listbox = tk.Listbox(self.frame, width=50, height=10, selectmode=tk.SINGLE)
        self.notification_listbox.grid(row=1, column=0, padx=10, pady=10)

        self.load_notifications()

        self.mark_read_button = ttk.Button(self.frame, text="Okundu Olarak İşaretle", command=self.mark_as_read)
        self.mark_read_button.grid(row=2, column=0, padx=10, pady=5)

        self.delete_button = ttk.Button(self.frame, text="Sil", command=self.delete_notification)
        self.delete_button.grid(row=3, column=0, padx=10, pady=5)

    def load_notifications(self):
        """Bildirimleri listele."""
        self.notification_listbox.delete(0, tk.END)
        notifications = self.notification_manager.get_notifications(self.username)
        self.notification_mapping = {i: notif["id"] for i, notif in enumerate(notifications)}
        for i, notif in enumerate(notifications):
            status = "[OKUNDU]" if notif["is_read"] == 1 else "[YENİ]"
            self.notification_listbox.insert(tk.END, f"{status} {notif['message']} (Zaman: {notif['timestamp']})")

    def mark_as_read(self):
        """Seçilen bildirimi okundu olarak işaretle."""
        try:
            selected_index = self.notification_listbox.curselection()[0]
            notification_id = self.notification_mapping[selected_index]
            self.notification_manager.mark_as_read(notification_id)
            self.load_notifications()
        except IndexError:
            messagebox.showwarning("Uyarı", "Lütfen okunacak bir bildirim seçin.")

    def delete_notification(self):
        """Seçilen bildirimi sil."""
        try:
            selected_index = self.notification_listbox.curselection()[0]
            notification_id = self.notification_mapping[selected_index]
            self.notification_manager.remove_notification(notification_id)
            self.load_notifications()
        except IndexError:
            messagebox.showwarning("Uyarı", "Lütfen silinecek bir bildirim seçin.")

# Kullanım Örneği
if __name__ == "__main__":
    # Veritabanı bağlantısını buraya ekleyin (conn veritabanı bağlantısı)
    conn = None  # Burada 'conn' nesnesi veritabanı bağlantısını temsil eder
    # Ana uygulamayı başlat
    root = tk.Tk()
    manager = NotificationManager(conn)  # Burada 'conn' bağlantısını kullanıyoruz
    app = UserNotificationsApp(root, manager, username="kullanici1")
    root.mainloop()
