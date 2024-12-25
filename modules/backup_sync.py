import os
import shutil

def sync_backup(src_dir, backup_dir):
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    for filename in os.listdir(src_dir):
        src_file = os.path.join(src_dir, filename)
        backup_file = os.path.join(backup_dir, filename)

        if os.path.isfile(src_file):
            shutil.copy(src_file, backup_file)

def monitor_changes(src_dir):
    # Change monitoring logic (e.g., using watchdog)
    pass
