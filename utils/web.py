from flask import jsonify, request, Request

from flask_login import UserMixin# https://ithelp.ithome.com.tw/articles/10328420
import requests
from datetime import datetime, timedelta

from socket import socket, AF_INET, SOCK_DGRAM
import requests

def get_latest_release(repo_name:str, repo_owner:str = 'timmy90928') -> tuple[str, str, str]:
    """
    Get the latest release information from GitHub.

    Returns: A tuple of (latest_version, latest_download_url, updated)
    """
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest'
    # https://api.github.com/repos/timmy90928/item_manager/releases/latest
    response = requests.get(url)
    if response.status_code == 200:
        release_info = response.json()              # Parse the JSON response.
        latest_version = release_info['tag_name']   # Get the latest version.
        assets = release_info['assets'][0]          # Get the download URL of the latest version.
        url = assets['browser_download_url']
        updated = datetime.strptime(assets['updated_at'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8)
        return latest_version, url, str(updated)
    
def return_page(success:str, message:str, state:int):
    return jsonify({"success": success, "message": message}), state

def get_local_ip():
    try:
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google Public DNS
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

def get_external_ip():
    try:
        # Use `ipify` to get external IP addresses
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()['ip']
    except Exception as e:
        return str(e)
    
def check_file(request:Request):
    if 'file' not in request.files:
        raise AssertionError('No file part')
    file = request.files['file']
    if file.filename == '':
        raise AssertionError('No selected file')
    return file