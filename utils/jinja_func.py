from flask import redirect
from flask_babel import gettext 
from typing import Union
from .web import Token
from .g import current
from .utils import now_time
def toInput(title:str = '輸入資料', action:str = '/input', datas:Union[dict, list[list]] = {'輸入': ['input', 'text']}, **args):
    """
    
    >>> <a href="{{ input('建立資料夾', '/tcloud/mkdir?path='~now_path, {'資料夾名稱': 'dirname'}) }}">建立資料夾</a>
    >>> <a href="{{ input('建立資料夾', '/tcloud/mkdir?path='~now_path, [['資料夾名稱', "<input name='' type='' id='' >"]] }})">建立資料夾</a>

    """
    # args = [f"<hiden name "]
    if isinstance(datas, dict):
        datas = [[key, f"<input name='{value[0] if isinstance(value, list) else value}' \
                                type='{value[1] if isinstance(value, list) else 'text'}' \
                                id='{value[0] if isinstance(value, list) else value}' >"] for key, value in datas.items()]
    data = {
        'datas': datas,
        'title': title,
        'action': action,
        'args': args
    }
    token = Token().generate(data)
    return f"/input?token={token}"

from flask import Flask
def initJinjaFunc(app:Flask, global_variables:dict = {}):
    """
    * input
    
    """
    for key, value in global_variables.items():
        app.jinja_env.globals[key] = value

    app.jinja_env.globals['input'] = toInput
    app.jinja_env.globals['current'] = current
    app.jinja_env.globals['str'] = str
    app.jinja_env.globals['now_time'] = now_time #? {{ now_time().split(' ')[0] }}
    app.jinja_env.globals['enumerate'] = enumerate
    app.jinja_env.globals['len'] = len
    # APP.jinja_env.filters

