from app import *

from flask import Flask
from flask import Blueprint
from flask import render_template
from flask import request
from flask import url_for
from flask import redirect
from flask import make_response
from flask import session #? session['key'] = 'value'
from flask import abort
from flask import send_from_directory
from flask import jsonify
from flask import Response
from flask import current_app
from flask import g

#? https://ithelp.ithome.com.tw/articles/10328420
from flask_login import login_user
from flask_login import login_required 
from flask_login import logout_user 

###* i18n ###
from flask_babel import lazy_gettext
from flask_babel import gettext
from flask_babel import ngettext

from os import listdir
from os import path
from os import stat
from os import remove 
from os import getcwd

###* utils ###
from utils.utils import *
from utils.web import *
from utils.g import *

###* Blueprint ###
from .root import root_bp
from .server import server_bp
from .accounting import accounting_bp
from .account import account_bp
from .travel import travel_bp
from .tcloud import tcloud_bp
from .record import record_bp

ALL_BP = [root_bp, server_bp, accounting_bp, account_bp, travel_bp, tcloud_bp, record_bp]


""""
https://dowyuu.github.io/program/2020/05/27/Input-Datalist/
"""

