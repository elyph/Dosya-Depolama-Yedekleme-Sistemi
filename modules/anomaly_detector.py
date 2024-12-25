import time

def detect_anomalies(logs):
    anomalies = []
    failed_logins = [log for log in logs if 'failed login' in log]

    if len(failed_logins) > 3:
        anomalies.append("Anormal giriş denemeleri tespit edildi.")

    # Diğer anormallik tespiti yapılabilir
    return anomalies
