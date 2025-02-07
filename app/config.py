from utils.utils import now_time as _now_time
from utils.utils import get_data_path as _get_data_path
from utils.utils import Path as _Path

APPNAME = 'Home'
DATAPATH = _get_data_path(APPNAME,['writable', 'log']) #? root_dir = getcwd()

def _create_sqlite_uri(abspath) -> str:
    return 'sqlite:///' + abspath

class BaseConfig:
    TITLE = APPNAME
    DESCRIPTION = 'Home management system'
    AUTHOR = 'WeiWen Wu'
    AUTHOR_EMAIL = 'timmy90928@gmail.com'
    GITHUB_URL = 'https://github.com/timmy90928/Home'
    COPYRIGHT = 'Copyright © 2024-2025 Wei-Wen Wu.All rights reserved'
    
    SERVER_RUN_TIME  = _now_time()
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024 # Set the maximum upload file size to 1024MB (1GB).

    LANGUAGES = ['zh_Hant_TW', 'en']
    BABEL_DEFAULT_LOCALE = 'zh_Hant_TW'

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    DATABASE_URI = str(_Path("./").joinpath('writable', "home.db").absolute())
    SQLALCHEMY_DATABASE_URI = _create_sqlite_uri(DATABASE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(BaseConfig):
    DEBUG = False
    DATABASE_URI = DATAPATH.get('writable', 'home.db')
    SQLALCHEMY_DATABASE_URI = _create_sqlite_uri(DATABASE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

configs = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}