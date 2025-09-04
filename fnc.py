# -*- coding: utf-8 -*-
import os
import zipfile
from pathlib import Path


def remove_file(file_path):
    try:
        os.remove(file_path)
        print(f"File '{file_path}' has been removed.")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except PermissionError:
        print(f"Error: Permission denied to remove file '{file_path}'.")
    except Exception as e:
        print(f"An error occurred while removing file '{file_path}': {e}")


def exists(path):
    file = Path(path)
    if file.is_file():
        return True
    else:
        return False


def add_file_to_zip(file_path, logs_dir, zip_file):
    zip_path = os.path.join(logs_dir, zip_file)
    if not os.path.exists(zip_path):
        # Create a new zip file if it doesn't exist
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.write(file_path, os.path.basename(file_path))
        print(f"Created {zip_path} and added {file_path}.")
    else:
        # Append to existing zip file and add the file
        with zipfile.ZipFile(zip_path, 'a') as zf:
            zf.write(file_path, os.path.basename(file_path))
        print(f"Appended {file_path} to {zip_path}.")


def add_files_to_zip(paths, logs_dir, zip_file, max_zip_size):
    # Check zip size
    zip_path = os.path.join(logs_dir, zip_file)
    if is_file_size_big(zip_path, max_zip_size):
        remove_file(zip_path)
    for file_path in paths:
        add_file_to_zip(file_path, logs_dir, zip_file)
        remove_file(file_path)


def get_file_size_log(file_path):
    file_size = None
    if exists(file_path):
        file_size = os.path.getsize(file_path)
    return file_size


def is_file_size_big(file_path, max_size):
    file_size = get_file_size_log(file_path)
    if file_size:
        if file_size > max_size:
            return True
        else:
            return False
    else:
        return False


def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

