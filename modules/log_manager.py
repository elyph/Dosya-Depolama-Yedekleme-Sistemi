import os
import time

def log_action(action, user):
    log_file = 'data/logs/actions.log'
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, 'a') as log:
        log.write(f"{timestamp} - {user}: {action}\n")

def read_logs():
    with open('data/logs/actions.log', 'r') as log_file:
        return log_file.readlines()
