from flask import Flask, Blueprint, render_template, request, url_for,redirect,make_response,session,abort,send_from_directory, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user as _current_user # https://ithelp.ithome.com.tw/articles/10328420
from os import listdir, path, stat, remove ,getcwd
from utils.db import database
from utils.utils import SysTray, json, now_time, timestamp
# from utils.web import User
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
app = Flask("Home")
systray = SysTray('Home')

### Configurations ###
app.secret_key = '62940eecccdf094995b09e1191b6e0afdcba8ee3293a5c893e146d0a5cf43210' # home-by-timmy90928
app.config['TITLE'] = 'Home'
app.config['DESCRIPTION'] = 'Home management system'
app.config['UPLOAD_FOLDER'] = path.join(getcwd(), 'writable') # Define the address of the upload folder.
app.config['SERVER_RUN_TIME'] = now_time()
app.config['VERSION'] = '1.0.0-beta.3'  # __version__ = ".".join(("0", "6", "3"))
app.config['AUTHOR'] = 'Wei-Wen Wu'
app.config['AUTHOR_EMAIL'] = 'timmy90928@gmail.com'
app.config['GITHUB_URL'] = 'https://github.com/timmy90928/Home'
app.config['COPYRIGHT'] = '(c) 2024 Wei-Wen Wu'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024 # Set the maximum upload file size to 1024MB (1GB).

login_manager = LoginManager(app)
login_manager.login_view = '/account/login'
db:database = database(path.join(app.config['UPLOAD_FOLDER'],'home.db'))
CONFIG = json(path.join(app.config['UPLOAD_FOLDER'],'config.json'))
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