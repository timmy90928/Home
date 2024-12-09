from flask import Flask, jsonify, request, Request, Response, abort
from json import dumps, load
from flask_login import UserMixin# https://ithelp.ithome.com.tw/articles/10328420
from requests import get as requests_get
from datetime import datetime, timedelta
from socket import socket, AF_INET, SOCK_DGRAM
import logging

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

def jsonify(obj):
    """
    Wrapper for flask.jsonify that formats the output nicely
    and ensures that the response is sent with the correct mimetype.

    :param obj: The object to be serialized into json
    :return: A flask.Response object with the json data
    """
    jsonify_config = {"sort_keys": False, "indent": 4,'ensure_ascii':False}
    json_data = dumps(obj, **jsonify_config)
    return Response(json_data, mimetype='application/json')

from typing import Optional, Callable, Any
from functools import wraps
def errorCallback(note:Optional[str]=None):
    
    def decorator(func:Callable):
        @wraps(func)
        def wrap(*args, **kwargs):
            try:
                return func(*args, **kwargs)   # print(func.__name__)
            except Exception as e:
                abort(500, description=f"[{e.__class__.__name__} ({func.__name__})] {e}",  response=note)
        return wrap
    return decorator

def set_file_handler(app:Flask, filename="log"):
    """
    Set a file handler for the app's logger to log messages to a file.

    The file will be named `<filename>.log` and will be created in the current working directory.
    The file will be appended to (not truncated) and will be encoded in utf-8.
    The format of the log messages will be `%(asctime)s >>> %(message)s` with the date and time in the format `%Y-%m-%d  %H:%M:%S`.

    The function will return the app's logger object.
    """
    app.logger.setLevel(logging.DEBUG)
    app.logger.handlers[0].setLevel(logging.WARNING)

    forfat_file = logging.Formatter(fmt='%(asctime)s >>> %(message)s',datefmt='%Y-%m-%d  %H:%M:%S') # (in %(filename)s:%(lineno)d)'

    file_handler = logging.FileHandler(filename=f"{filename}.log", mode='a', encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt=forfat_file)  # Add Formatting.

    app.logger.addHandler(file_handler)

    return app.logger