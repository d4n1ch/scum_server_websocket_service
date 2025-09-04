# -*- coding: utf-8 -*-
import json
import os.path
import secrets
import configparser
from logger import log, logs_dir
from fnc import exists, create_directory

section = 'settings'

"""
    Read variables from configs
"""
config_path = './config'
file_client_config = 'client_config.ini'
file_server_config = 'server_config.ini'
file_query_queue = 'query_queue.json'

file_client_config_path = os.path.join(config_path, file_client_config)
file_server_config_path = os.path.join(config_path, file_server_config)
file_query_queue_path = os.path.join(config_path, file_query_queue)

# Create directories

if not exists(config_path):
    create_directory(config_path)

if not exists(logs_dir):
    create_directory(logs_dir)

if not exists(file_client_config_path):
    secure_token = secrets.token_urlsafe(32)
    config = configparser.ConfigParser()
    config['config'] = {
        'auth_token': secure_token
    }
    with open(file_client_config_path, 'w') as configfile:
        config.write(configfile)
    log(section, f"[v] Config {file_client_config} created with auth_token: {secure_token}")

if not exists(file_server_config_path):
    config = configparser.ConfigParser()
    config['config'] = {
        'wss_ip': '0.0.0.0',
        'wss_port': '7778',
        'scum_db': '../Saved/SaveFiles/SCUM.db'
    }
    with open(file_server_config_path, 'w') as configfile:
        config.write(configfile)
    log(section, f"[v] Config {file_server_config_path} created")

if not exists(file_query_queue_path):
    dictionary = {}
    with open(file_query_queue_path, 'w') as file:
        file.write(json.dumps(dictionary))
    log(section, f"[v] Config {file_query_queue_path} created")

try:
    config_client = configparser.ConfigParser()
    config_client.read(file_client_config_path)
    config_server = configparser.ConfigParser()
    config_server.read(file_server_config_path)
    log(section, '[v] Loaded configs')
    auth_token = config_client['config']['auth_token']
    log(section, f'[v] auth_token: {auth_token}')
    wss_ip = config_server['config']['wss_ip']
    log(section, f'[v] wss_ip: {wss_ip}')
    wss_port = int(config_server['config']['wss_port'])
    log(section, f'[v] wss_port: {wss_port}')
    scum_db = config_server['config']['scum_db']
    log(section, f'[v] scum_db: {scum_db}')
except (Exception, IOError) as e:
    log(section, f"[x] EXCEPTION: Couldn't load configs: {e}")
