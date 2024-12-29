import time
import threading
import datetime

class UserBehaviorWatcher:
    def __init__(self, log_file, alert_callback):
        self.log_file = log_file
        self.alert_callback = alert_callback  # Uyarı callback fonksiyonu
        self.failed_login_attempts = {}  # Kullanıcı bazında başarısız giriş denemeleri
        self.password_change_requests = {}  # Kullanıcı bazında parola değiştirme talepleri

    def read_log_file(self):
        """Log dosyasını satır satır oku."""
        try:
            with open(self.log_file, "r") as log:
                while True:
                    line = log.readline()
                    if not line:
                        time.sleep(1)
                        continue
                    self.process_log_line(line)
        except FileNotFoundError:
            print(f"Hata: {self.log_file} dosyası bulunamadı.")
        except Exception as e:
            print(f"Hata: {str(e)}")

    def process_log_line(self, line):
        """Log satırında anormal davranışları kontrol et."""
        if "failed login" in line:
            self.handle_failed_login(line)
        elif "password change" in line:
            self.handle_password_change(line)

    def handle_failed_login(self, line):
        """Başarısız giriş denemelerini takip et."""
        user = self.extract_user_from_line(line)
        if user:
            if user not in self.failed_login_attempts:
                self.failed_login_attempts[user] = 0
            self.failed_login_attempts[user] += 1
            if self.failed_login_attempts[user] >= 3:  # 3 başarısız giriş
                self.alert_callback(f"Anormal Davranış: Kullanıcı {user} 3'ten fazla başarısız giriş yaptı.")

    def handle_password_change(self, line):
        """Kullanıcının parola değiştirme taleplerini takip et."""
        user = self.extract_user_from_line(line)
        if user:
            current_time = datetime.datetime.now()
            if user not in self.password_change_requests:
                self.password_change_requests[user] = []
            self.password_change_requests[user].append(current_time)

            # 1 saat içinde yapılan taleplerin listesini temizle
            self.password_change_requests[user] = [
                time for time in self.password_change_requests[user] if (current_time - time).seconds < 3600
            ]
            
            # Eğer 1 saat içinde 3 talep varsa uyarı gönder
            if len(self.password_change_requests[user]) >= 3:
                self.alert_callback(f"Anormal Davranış: Kullanıcı {user} 1 saat içinde 3 kez parola değiştirdi.")

    def extract_user_from_line(self, line):
        """Log satırından kullanıcı bilgilerini çıkar."""
        try:
            if "user=" in line:
                return line.split("user=")[1].split()[0]
        except IndexError:
            pass  # Eğer kullanıcı bilgisi çıkarılamazsa, sadece geçiyoruz
        return None

    def start(self):
        """Log dosyasını izlemeye başla."""
        threading.Thread(target=self.read_log_file, daemon=True).start()
