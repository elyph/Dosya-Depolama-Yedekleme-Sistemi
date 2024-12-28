import time
import threading
import shutil
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from tkinter import ttk
from tkinter import Tk, Label, Button

# Dosya izleme işlemi için event handler
class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, source_dir, backup_dir, progress_bar):
        self.source_dir = source_dir
        self.backup_dir = backup_dir
        self.progress_bar = progress_bar

    def on_modified(self, event):
        if event.is_directory:
            return
        print(f"Değişiklik algılandı: {event.src_path}")
        self.backup_files()

    def on_created(self, event):
        if event.is_directory:
            return
        print(f"Yeni dosya eklendi: {event.src_path}")
        self.backup_files()

    def backup_files(self):
        # Yedekleme işlemi başlatılır
        threading.Thread(target=self.perform_backup).start()

    def perform_backup(self):
        # Yedekleme işlemi burada yapılır
        self.progress_bar['value'] = 0
        files = os.listdir(self.source_dir)
        total_files = len(files)
        
        for idx, file in enumerate(files):
            src_path = os.path.join(self.source_dir, file)
            dest_path = os.path.join(self.backup_dir, file)
            
            if os.path.isfile(src_path):
                shutil.copy(src_path, dest_path)
                time.sleep(0.1)  # Yedekleme süresi
                self.progress_bar['value'] = ((idx + 1) / total_files) * 100
                time.sleep(0.1)  # Geriye doğru işlem yapılmasını engellemek için

        print("Yedekleme tamamlandı!")

# Yedekleme işlemi için ana sınıf
class FileBackupApp:
    def __init__(self, root, source_dir, backup_dir):
        self.root = root  # `root` parametresini burada alıyoruz
        self.source_dir = source_dir
        self.backup_dir = backup_dir
        self.progress_bar = None

        # Yedekleme işlemini başlatıyoruz
        self.start_backup_sync()

    def start_backup_sync(self):
        # UI elemanları
        label = Label(self.root, text="Yedekleme İlerleme", font=("Arial", 14))
        label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)

        # Dosya izleyici başlatma
        handler = FileChangeHandler(self.source_dir, self.backup_dir, self.progress_bar)
        observer = Observer()
        observer.schedule(handler, self.source_dir, recursive=True)
        observer.start()

        # Dosya izleme işlemi ve yedekleme işlemi başlatılır
        handler.backup_files()  # Bu, hemen başlatılacak

        # Uygulamanın sürekli çalışmasını sağlamak için mainloop
        self.root.mainloop()

if __name__ == "__main__":
    root = Tk()
    source_dir = "../modules/source"  # Kaynak dizin yolu
    backup_dir = "../modules/backup"  # Yedekleme dizin yolu
    app = FileBackupApp(root, source_dir, backup_dir)
