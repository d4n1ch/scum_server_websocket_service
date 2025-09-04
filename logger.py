# -*- coding: utf-8 -*-
import os
import glob
import datetime
from fnc import exists, create_directory, add_files_to_zip, is_file_size_big

log_level = 0

logs_dir = './logs'
max_log_size = 104857600  # size in bytes 104857600 is 100 Megabytes
max_zip_size = 262144000  # size in bytes 262144000 is 250 Megabytes

zip_file = "logs.zip"

filename_date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')
file_name = f'sswss_log_{filename_date}.log'
file_name_critical = f'sswss_log_critical_{filename_date}.log'

file_filter = '*.log'
files_path = os.path.join(logs_dir, file_filter)
files_logs = sorted(glob.glob(files_path))
add_files_to_zip(files_logs, logs_dir, zip_file, max_zip_size)


def archive_and_rotate():
    global file_name, file_name_critical
    prev_file_name = os.path.join(logs_dir, file_name)
    prev_file_name_critical = os.path.join(logs_dir, file_name_critical)
    new_filename_date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')
    file_name = f'sswss_log_{new_filename_date}.log'
    file_name_critical = f'sswss_log_critical_{new_filename_date}.log'
    log_write_critical('New file', os.path.join(os.path.join(os.getcwd(), logs_dir), file_name_critical))
    log_paths = [prev_file_name, prev_file_name_critical]
    date_now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    log_text = f'[{date_now}][archive_and_rotate][ Begin archiving log files ]'
    print(log_text)
    add_files_to_zip(log_paths, logs_dir, zip_file, max_zip_size)
    date_now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    log_text = f'[{date_now}][archive_and_rotate][ Return new log file: {file_name} ]'
    print(log_text)
    return os.path.join(os.path.join(os.getcwd(), logs_dir), file_name)


def log_write(log_text, file_path):
    if exists(file_path):
        try:
            if not is_file_size_big(file_path, max_log_size):
                fp = open(os.path.abspath(file_path), 'a', encoding='utf-8')
                fp.write(log_text + '\n')
                fp.close()
            else:
                new_path = archive_and_rotate()
                fp = open(os.path.abspath(new_path), 'a', encoding='utf-8')
                fp.write(log_text + '\n')
                fp.close()
        except (IOError, Exception) as errors:
            print(errors)
    else:
        try:
            create_directory(os.path.join(os.getcwd(), logs_dir))
            fp = open(os.path.abspath(file_path), 'w', encoding='utf-8')
            fp.write(log_text + '\n')
            fp.close()
        except (IOError, Exception) as errors:
            print(errors)


def log_write_critical(log_text, file_path_critical):
    if exists(file_path_critical):
        try:
            fp = open(os.path.abspath(file_path_critical), 'a', encoding="utf8")
            fp.write(log_text + '\n')
            fp.close()
        except (IOError, Exception) as errors:
            print(errors)
    else:
        try:
            create_directory(os.path.join(os.getcwd(), logs_dir))
            fp = open(os.path.abspath(file_path_critical), 'w', encoding="utf8")
            fp.write(log_text + '\n')
            fp.close()
        except (IOError, Exception) as errors:
            print(errors)


def log(section, text):
    global log_level
    file_path = os.path.join(os.path.join(os.getcwd(), logs_dir), file_name)
    file_path_critical = os.path.join(os.path.join(os.getcwd(), logs_dir), file_name_critical)
    text = str(text)
    date_now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    log_text = f'[{date_now}][{section}][ {text} ]'
    critical = False
    if "exception" in text.lower() or "traceback" in text.lower():
        critical = True
    try:
        if log_level == 0:
            print(log_text)
            log_write(log_text, file_path)
            if critical:
                log_write_critical(log_text, file_path_critical)
        elif log_level == 1:
            print(log_text)
            if critical:
                log_write_critical(log_text, file_path_critical)
        elif log_level == 2:
            print(log_text)
        else:
            pass
    except (IOError, Exception) as errors:
        print(errors)