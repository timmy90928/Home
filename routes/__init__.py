from flask import Flask, Blueprint, render_template, request, url_for,redirect,make_response,session,abort,send_from_directory, jsonify, Response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user as _current_user # https://ithelp.ithome.com.tw/articles/10328420
from os import listdir, path, stat, remove ,getcwd
from utils.db import database
from utils.utils import SysTray, json, now_time, timestamp, get_data_path
from utils.web import errorCallback, set_file_handler
from time import time

class User(UserMixin):
    # def __init__(self, user_id:int, user_name:str, nickname:str, role:str = 'admin'):
    def __init__(self,user_id:int):
        user_id = int(user_id)
        if user_id == 0:
            username,name,role = 'developer','Developer','developer'
        else:
            try:  username,name,role = db.get_row('account', ['id',user_id],'username,name,role')[0]
            except Exception as e:  username,name,role = 'error',e,'error'

        self.id:int = user_id
        self.username = username
        self.name = name
        self.role = role
        self.rolenum = roles[role]

### Main App ###
APPNAME = 'Home'
app = Flask(APPNAME)
systray = SysTray(APPNAME)
DATAPATH = get_data_path(APPNAME,['writable', 'log']) # root_dir = getcwd() 
CONFIG = json(DATAPATH.get('writable', 'config.json'))

### Configurations ###
app.secret_key = '62940eecccdf094995b09e1191b6e0afdcba8ee3293a5c893e146d0a5cf43210' # home-by-timmy90928
app.config['TITLE'] = APPNAME
app.config['DESCRIPTION'] = 'Home management system'
app.config['UPLOAD_FOLDER'] = DATAPATH.get('writable') # Define the address of the upload folder.
app.config['tcloud'] = CONFIG.get('base/tcloud', "./")
app.config['SERVER_RUN_TIME'] = now_time()
app.config['VERSION'] = 'v1.0.0-beta.5'  # __version__ = ".".join(("0", "6", "3"))
app.config['AUTHOR'] = 'Wei-Wen Wu'
app.config['AUTHOR_EMAIL'] = 'timmy90928@gmail.com'
app.config['GITHUB_URL'] = 'https://github.com/timmy90928/Home'
app.config['COPYRIGHT'] = '(c) 2024 Wei-Wen Wu'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024 # Set the maximum upload file size to 1024MB (1GB).

LOG = set_file_handler(app, DATAPATH.get('log', f"log-{app.config['VERSION']}")) # Logger
db:database = database(DATAPATH.get('writable', 'home.db'))

login_manager = LoginManager(app)
login_manager.login_view = '/account/login'
current_user:User = _current_user
clients = {}

### Request decorator ###
@app.context_processor
def inject_global_vars():
    """Injects global variables to all templates."""
    try:
        name = current_user.name 
    except: 
        name = ''
    return {
        'site_header_title': CONFIG('server/SITE_HEADER_TITLE'),
        'login_user_name': name, #  current_user.id
    }

@app.before_request
def track_connection() -> None:
    """Tracks all the current clients (by IP) and stores them in the set clients."""
    ip = request.remote_addr
    clients[ip] = time()

@app.after_request
def log_status_code(response:Response):
    ip = request.remote_addr
    page = request.path
    method = request.method
    status_code = response.status_code

    if status_code != 304: LOG.debug(f'{status_code} >>> {method:^5} >>> {ip:^12} >>> {page}')
    return response

@app.teardown_request
def remove_client(exc=None):
    """Removes the client from the set clients when the request is finished."""
    for ip, timestamp in list(clients.items()):
        if time() - timestamp > 300:  # 5 minutes
            del clients[ip]

@login_manager.user_loader
def load_user(username):
    # user_data = 1#users.get(user_id)
    return User(username)



### Blueprint ###
from .root import root_bp
from .server import server_bp
from .accounting import accounting_bp
from .account import account_bp
from .travel import travel_bp

ALL_BP = [root_bp, server_bp, accounting_bp, account_bp, travel_bp]

from enum import IntEnum 
class roles(IntEnum):
    developer = 0
    admin = 1
    user = 2
    viewer = 3
    error = 9

""""
https://dowyuu.github.io/program/2020/05/27/Input-Datalist/
"""

from werkzeug.exceptions import HTTPException
@app.errorhandler(HTTPException)
def all_error_handler(e:HTTPException):
    # abort(status_code, response=f"{status_code}")
    page = [
        ['HTTP狀態碼', e.code],
        ['HTTP狀態', e.name],
        ['錯誤訊息', str(e.description)],
        ['回覆(response)', str(e.response)],
        ['標頭(headers)', str(e.get_headers())],
        ['參數(args)', str(e.args if e.args else '')],
    ]
    return render_template('common/list.html',title=f"{e.code}-{e.name}",datas=page,heads=['key', 'value']), e.code