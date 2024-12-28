import os
from datetime import datetime

class LogWatcher:
    def __init__(self):
        # Log dosyalarının kaydedileceği dizin
        self.log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)

    def log(self, category, action_code, status_code, details, data_size=0):
        """Genel bir log kaydı yapar."""
        # Log dosyasının adı, kategoriye göre belirlenir
        log_file = os.path.join(self.log_dir, f'{category}_log.txt')

        # Şu anki tarih ve saat
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Log formatı
        log_message = (
            f"{current_time} | Action Code: {action_code} | Status Code: {status_code} | "
            f"Details: {details} | Data Size: {data_size}MB"
        )

        # Log kaydını dosyaya ekle
        with open(log_file, 'a') as file:
            file.write(log_message + '\n')

        # Konsola log mesajını yazdır
        print(log_message)

    def log_anomaly(self, anomaly_type, username, **kwargs):
        """
        Anormal durumları loglar.
        
        Parameters:
        - anomaly_type (str): Anomali türü (ör. 'UNEXPECTED_INTERRUPTION').
        - username (str): Kullanıcı adı.
        - kwargs: Anomali türüne bağlı ek bilgiler.
        """
        log_file = os.path.join(self.log_dir, 'anomaly_log.txt')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        description = ""

        if anomaly_type == "UNEXPECTED_INTERRUPTION":
            operation = kwargs.get("operation", "Unknown Operation")
            status = kwargs.get("status", "UNKNOWN")
            description = f"{operation} operation was interrupted unexpectedly. Status: {status}."
        
        elif anomaly_type == "UNUSUAL_FILE_ACTIVITY":
            activity_type = kwargs.get("activity_type", "Unknown Activity")
            count = kwargs.get("count", 0)
            time_period = kwargs.get("time_period", "Unknown Period")
            description = f"{count} {activity_type} operations detected within {time_period} seconds."

        elif anomaly_type == "UNAUTHORIZED_SHARING":
            file_name = kwargs.get("file_name", "Unknown File")
            recipient = kwargs.get("recipient", "Unknown Recipient")
            description = f"Attempted to share '{file_name}' with unauthorized user {recipient}."

        elif anomaly_type == "FAILED_LOGIN_ATTEMPTS":
            attempts = kwargs.get("attempts", 0)
            time_period = kwargs.get("time_period", "Unknown Period")
            description = f"{attempts} failed login attempts detected within {time_period} seconds."

        elif anomaly_type == "FREQUENT_PASSWORD_REQUESTS":
            request_count = kwargs.get("request_count", 0)
            time_period = kwargs.get("time_period", "Unknown Period")
            description = f"{request_count} password change requests detected within {time_period} seconds."

        else:
            description = "Unknown anomaly detected."

        log_message = f"{current_time} | Anomaly Type: {anomaly_type} | Username: {username} | Description: {description}"

        # Log kaydını dosyaya ekle
        with open(log_file, 'a') as file:
            file.write(log_message + '\n')
        
        print(log_message)

    # Takım üyesi belirleme
    def log_team_member_assignment(self, username, team_member, status):
        """Takım üyesi belirleme işlemini loglar."""
        self.log(
            'team_member_assignment',
            'TEAM_MEMBER_ASSIGNMENT',
            status,
            f"Assigned team member: {team_member} by {username}"
        )

    # Doküman paylaşımı
    def log_document_sharing(self, username, document_name, recipient, status):
        """Doküman paylaşımı işlemini loglar."""
        self.log(
            'document_sharing',
            'DOCUMENT_SHARING',
            status,
            f"User {username} shared document '{document_name}' with {recipient}"
        )

    # Parola değiştirme talebi
    def log_password_change_request(self, username, status):
        """Parola değiştirme talebini loglar."""
        self.log(
            'password_change_request',
            'PASSWORD_CHANGE_REQUEST',
            status,
            f"User {username} requested a password change"
        )

    # Parola değiştirme talebi onaylama
    def log_password_change_approval(self, admin_username, username, status):
        """Parola değiştirme talebinin onaylanmasını loglar."""
        self.log(
            'password_change_approval',
            'PASSWORD_CHANGE_APPROVAL',
            status,
            f"Admin {admin_username} approved password change for {username}"
        )

    # Profil girişleri
    def log_profile_login(self, username):
        """Kullanıcı profil girişlerini loglar."""
        self.log(
            'profile_login',
            'PROFILE_LOGIN',
            'SUCCESS',
            f"User {username} logged into their profile"
        )

    # Yedekleme işlemi
    def log_backup(self, status, message):
        """Yedekleme işlemi log kaydını yapar."""
        self.log(
            'backup',
            'BACKUP',
            status,
            message
        )
