from flask_login import UserMixin as _UserMixin
from flask_login import current_user as _current_user 
from enum import IntEnum as _IntEnum


class roles(_IntEnum):
    developer = 0
    admin = 1
    user = 2
    viewer = 3
    error = 9

class User(_UserMixin):
    #? def __init__(self, user_id:int, user_name:str, nickname:str, role:str = 'admin'):
    def __init__(self,user_id:int):
        user_id = int(user_id)
        if user_id == 0:
            username,name,role = 'developer','Developer','developer'
        else:
            try:  username,name,role = current.db.get_row('account', ['id',user_id],'username,name,role')[0]
            except Exception as e:  username,name,role = 'error',e,'error'

        self.id:int = user_id
        self.username = username
        self.name = name
        self.role = role
        self.rolenum = roles[role]
current_user:User = _current_user

### current ###
from utils.db import database
from utils.utils import json
from logging import Logger
class Current:
    _current_db = None
    _current_config = None
    _current_log = None
    _current_other:dict = {}
    def __new__(cls):
        if not hasattr(cls,'_instance'): 
            setattr(cls,'_instance',super().__new__(cls))
        return getattr(cls,'_instance')

    def _checkNone(self,name:str):
        if not getattr(self,f"_current_{name}"):
            raise NameError(f'Undefined {name}.')
    def _checkType(self,obj: object, type:object):
        if not isinstance(obj, type):
            raise TypeError(f'Type must be a {type}.')
    
    def __getitem__(self, key):
        if key not in self._current_other: raise NameError(f'Undefined {key}.')
        return self._current_other[key]
    
    def __setitem__(self, key, value):
        self._current_other[key] = value

    def __delitem__(self, key):
        del self._current_other[key]

    @property
    def config(self) -> json:
        self._checkNone('config')
        return self._current_config
    
    @config.setter
    def config(self,config):
        self._checkType(config, json)
        self._current_config = config

    @property
    def db(self) -> database:
        self._checkNone('db')
        return self._current_db
    
    @db.setter
    def db(self,db):
        self._checkType(db, database)
        self._current_db = db
        
    @property
    def log(self) -> Logger:
        self._checkNone('log')
        return self._current_log
    
    @log.setter
    def log(self,log):
        self._checkType(log, Logger)
        self._current_log = log

current = Current()
clients = {}


