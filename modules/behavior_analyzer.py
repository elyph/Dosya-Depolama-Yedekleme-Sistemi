def analyze_user_behavior(user_logs):
    failed_logins = [log for log in user_logs if 'failed login' in log]

    if len(failed_logins) > 3:
        return "Anormal giriş davranışı tespit edildi."

    return "Davranış normal."
