
from .config import configs
from .config import APPNAME
from .config import DATAPATH
from .admin import initAdmin
from .admin import Admin as FlaskAdmin
from .model import initDB

###* Global Variable ###
from utils.g import clients
from utils.g import current

###* Type Hinting ###
from typing import Literal
from flask import Response

###* Standard Library ###
from flask import Flask
from flask import session
from flask import render_template
from flask import request
from time import time
from flask_babel import Babel

###* Tools ###
from utils.jinja_func import initJinjaFunc
from utils.utils import SysTray, json, get_data_path
from utils.web import errorCallback, set_file_handler, Token
from utils.db import database

###* Main App ###
APP = Flask(APPNAME)
systray = SysTray(APPNAME) 
current.config = json(DATAPATH.get('writable', 'config.json'))

###* Configurations ###
#! SECRET_KEY & VERSION
APP.secret_key = '62940eecccdf094995b09e1191b6e0afdcba8ee3293a5c893e146d0a5cf43210' # home-by-timmy90928
APP.config['UPLOAD_FOLDER'] = DATAPATH.get('writable') # Define the address of the upload folder.
APP.config['tcloud'] = current.config.get('base/tcloud', "../")
APP.config['VERSION'] = 'v1.0.0-beta.5'  # __version__ = ".".join(("0", "6", "3"))

###* Login Manager ###
from flask_login import LoginManager
login_manager = LoginManager(APP)
login_manager.login_view = '/account/login'

###* Request decorator ###
@APP.context_processor
def inject_global_vars():
    """Injects global variables to all templates."""
    try:
        from utils.g import current_user
        name = current_user.name 
    except: 
        name = ''
    return {
        'site_header_title': current.config('server/SITE_HEADER_TITLE'),
        'login_user_name': name, #  current_user.id
    }

@APP.before_request
def track_connection() -> None:
    """Tracks all the current clients (by IP) and stores them in the set clients."""
    ###* i18n ###
    lang = request.cookies.get('lang') if request.cookies.get('lang') else request.accept_languages.best_match(APP.config['LANGUAGES'])
    session['lang'] = lang

    ip = request.remote_addr
    clients[ip] = time()

@APP.after_request
def log_status_code(response:Response):
    ###* i18n ###
    response.set_cookie('lang', session['lang'], max_age=60*60*24)

    ###* Logger ###
    ip = request.remote_addr
    page = request.path
    method = request.method
    status_code = response.status_code

    if status_code != 304: current.log.debug(f'{status_code} >>> {method:^5} >>> {ip:^12} >>> {page}')
    return response

@APP.teardown_request
def remove_client(exc=None):
    """Removes the client from the set clients when the request is finished."""
    for ip, timestamp in list(clients.items()):
        if time() - timestamp > 300:  # 5 minutes
            del clients[ip]

@login_manager.user_loader
def load_user(username):
    from utils.g import User
    # user_data = 1#users.get(user_id)
    return User(username)

from werkzeug.exceptions import HTTPException
@APP.errorhandler(HTTPException)
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

def get_locale():
    lang_a = request.args.get('lang')
    lang = lang_a if lang_a else session.get('lang','en')
    return lang

def create_app(config_name:Literal['development', 'production'] = 'development'):
    global APP

    ###* Configurations ###
    APP.config.from_object(configs[config_name])
    babel = Babel(APP, locale_selector=get_locale)
    version_update = not bool(current.config.get("server/VERSION") == APP.config['VERSION'])
    # print(version_update)
    current.log = set_file_handler(APP, DATAPATH.get('log', f"log-{APP.config['VERSION']}")) # Logger
    current.db = database(APP.config['DATABASE_URI'])
    
    ###* Init Tools ###
    initDB(APP)         # Database (SQLAlchemy)
    initJinjaFunc(APP)  # Jinja2
    initAdmin(APP)      # Admin View

    ###* Register Blueprint ###
    from routes import ALL_BP
    for bp in ALL_BP:
        APP.register_blueprint(bp)

    ###* System Tray Icon ###
    if not APP.debug:
        systray.start()

    return APP