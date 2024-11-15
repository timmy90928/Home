from flask import jsonify, request, Request

from flask_login import UserMixin# https://ithelp.ithome.com.tw/articles/10328420
from requests import get as requests_get
from datetime import datetime, timedelta
from socket import socket, AF_INET, SOCK_DGRAM

def get_latest_release(repo_name:str, repo_owner:str = 'timmy90928') -> tuple[str, str, str]:
    """
    Get the latest release information from GitHub.

    Returns: A tuple of (latest_version, latest_download_url, updated)

    >>> latest_version,web,[url, size, updated] = get_latest_release('Home')
    """
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest'
    # https://api.github.com/repos/timmy90928/Home/releases/latest
    response = requests_get(url)
    if response.status_code == 200:
        release_info = response.json()              # Parse the JSON response.
        latest_version = release_info['tag_name']   # Get the latest version.
        web = release_info['html_url']              # Get the HTML URL of the latest version.

        ### Assets
        assets = release_info['assets'][0]          # Get the download URL of the latest version.
        url = assets['browser_download_url']
        updated = datetime.strptime(assets['updated_at'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8)
        size = assets['size']
        return latest_version, web, [url, size, str(updated)]

def download_file(url:str, dest:str, stream:bool=False, **kwargs):
    response = requests_get(url, stream=stream, **kwargs) 
    if response.status_code == 200:
        with open(dest, 'wb') as f:
            f.write(response.content)
    else:
        raise Exception(f"Failed url: {url}")
    
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
        response = requests_get('https://api.ipify.org?format=json')
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
