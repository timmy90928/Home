from datetime import timedelta,datetime,timedelta
from shutil import copy2, rmtree, ignore_patterns, copytree
from os import environ,mkdir
from os.path import isfile, isdir, split as path_split,join, abspath, exists
from base64 import b64encode,b64decode
from urllib.parse import quote, unquote
from typing import Any, Union, Optional, Callable
import math
from hashlib import sha3_256
from json import load, dump
from pystray import MenuItem, Icon as _icon, Menu as StrayMenu
from PIL import Image
from threading import Thread
import webbrowser
from typing import overload, Literal, Optional

def hash(text:str) -> str:
    """
    Hash the text using SHA3-256.

    ## Example
    >>> hash('home')
    'a20243f409be1afca9a63f66224b3467eaa9194753561e33b4d1202294cabd21'
    """
    return sha3_256(text.encode()).hexdigest()

class json:
    """
    ### Example
    ```
    from utils.utils import json
    _json = json('static/config.json')
    print(_json('base/UPLOAD_FOLDER'))
    _json_data = _json.load()
    print(_json_data['success'])
    _json_data['success'] = False
    _json.dump(_json_data)
    ```
    """
    def __init__(self, path:str) -> None:
        self.path = path

    @overload
    def __call__(self, key:str) -> Any: 
        """
        Get the value of the specified key in the JSON file.

        ### Example
        >>> _json('base/UPLOAD_FOLDER')
        """
    ...
    @overload
    def __call__(self, key:str, value:Any) -> dict: 
        """
        Set the value of the specified key in the JSON file.

        ### Example
        >>> _json('base/UPLOAD_FOLDER', 'new/path')
        """
    ...
    def __call__(self, key:str, value = None):
        keys = key.split('/')
        if value: 
            result = self._set(keys, value)
            self.dump(result)
            return result
        else:
            return self._get(keys)

    def get(self, key:str, default = None):
        keys = key.split('/')
        try:
            return self._get(keys)
        except KeyError:
            result = self._set(keys, default)
            self.dump(result)
            return default

    def _set(self, keys:list, value:Any) -> dict:
        temp =  self.load().copy()
        _ = "temp"
        for k in keys:
            if k == '': continue
            _ += f"['{k}']"
        exec(f"{_} = value")
        return temp
        
    def _get(self, keys:list) -> Any:

        self.data = self.load()
        result = self.data.copy()
        for k in keys:
            if k == '': continue
            result = result[k]
        return result
    def load(self) -> dict:
        with open(self.path, 'r', encoding='utf-8') as f:
            return load(f)

    def dump(self, data:dict) -> bool:
        with open(self.path, 'w', encoding='utf-8') as f:
            dump(data, f, ensure_ascii=False, indent=4)
        return True

from time import sleep
class SysTray(_icon):
    """
    >>> tray = SysTray('Title')
    >>> tray.title
    'Title'
    """
    def __init__(self, name):
        super().__init__(name=name, title=name, icon=self.create_image(), menu=self.create_menu())

    def start(self):
        Thread(target=self.run, daemon=False).start()
        sleep(0.05)
        self.notify("伺服器已啟動","啟動通知")

    def create_image(self):
        image = Image.open("static/picture/house.ico")
        return image
    
    def create_menu(self):
        return StrayMenu(
            MenuItem("管理伺服器", self.open_sever_info),
            MenuItem("顯示IP", self.show_ip),
            MenuItem("結束", self.on_quit),
            )

    def on_quit(self, icon, item):
        self.notify("伺服器已關閉","結束通知")
        self.stop()
        exit(0)
    
    def show_ip(self, icon, item):
        from utils.web import get_external_ip, get_local_ip
        self.notify(f"內網IP:{get_local_ip()}\n外網IP:{get_external_ip()}","IP通知")
        return True
    
    def open_sever_info(self, icon, item):
        webbrowser.open('http://localhost:928/server/info')


def msgw(title:str="Title", text:str="contant", style:int=0, time:int=0) -> int:
    """
    ctypes.windll.user32.MessageBoxTimeoutW()

    Styles
    ------
    ```
    0 : OK
    1 : OK | Cancel
    2 : Abort | Retry | Ignore
    3 : Yes | No | Cancel
    4 : Yes | No
    5 : Retry | No 
    6 : Cancel | Try Again | Continue
    ```

    Example
    -------
    >>> msg=msgw('title','contant',0,1)  # time (ms)
    """
    import ctypes
    # MessageBoxTimeoutW(父窗口句柄,消息內容,標題,按鈕,語言ID,等待時間)
    return ctypes.windll.user32.MessageBoxTimeoutW(0, text, title, style,0,time)

def now_time(_format = '%Y-%m-%d %H:%M:%S') -> str:
    """
    ## Example
    >>> now_time() # doctest: +SKIP
    '2022-08-31 23:59:59'
    """
    return datetime.now().strftime(_format)

@overload
def timestamp(string: str) -> float:...
@overload
def timestamp(ts: Union[int,float]) -> str:...
@overload
def timestamp(year: int, month: int, day: int = 1, hour: int = 0, minute: int = 0, second: int = 0, dday: int = 0, dhour: int = 0, dminute: int = 0, dsecond: int = 0) -> float:...
def timestamp(year=1999, month=1, day=1, hour=0, minute=0, second=0, dday=0, dhour=0, dminute=0, dsecond=0, ts:Union[int,float] = None, string:str = None) -> float:
    """
    ## Example
    >>> timestamp(2024,10+1,dsecond=-1)
    1730390399.0
    >>> timestamp(string='2024-10-31 23:59:59')
    1730390399.0
    >>> timestamp(ts=1730390399.0)
    '2024-10-31 23:59:59'
    """
    if ts:
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    elif string:
        arr_string = string.split(" ")
        if len(arr_string) == 1:
            arr = arr_string[0].split("-")
            return timestamp(year=int(arr[0]), month=int(arr[1]), day=int(arr[2]))
        else:
            arr0 = arr_string[0].split("-")
            arr1 = arr_string[1].split(":")
            return timestamp(year=int(arr0[0]), month=int(arr0[1]), day=int(arr0[2]),hour=int(arr1[0]), minute=int(arr1[1]), second=int(arr1[2]))
    else:
        dt = timedelta(days=dday, hours=dhour, minutes=dminute, seconds=dsecond)
        if int(month) > 12: year, month = int(year)+1, int(month)-12
        t = datetime.strptime(f'{year:04}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02}', "%Y-%m-%d %H:%M:%S") + dt
        return t.timestamp()


def copy(src:str, dst:str, ignore:list = [], return_format:str = '{mode}: {src} -> {dst}') -> str:
    """
    Copies a file from the `src` path to the `dst` path.

    :param src: The source file path. Must be a Path object.('./writable/home.db')
    :param dst: The destination file path. Must be a Path object.

    >>> copy()
    Traceback (most recent call last):
    ...
    TypeError: copy() missing 2 required positional arguments: 'src' and 'dst'
    """
    if not src or not dst:
        raise ValueError("Both src and dst must be non-empty")
    try:
        if isdir(src):
            mode = 'dir'
            dst = join(dst,path_split(src)[-1])
            copytree(src, dst, ignore=ignore_patterns(*ignore), dirs_exist_ok=True)
        elif isfile(src):
            mode = 'file'
            copy2(src, dst)
        else:
            raise ValueError(f"{src} is neither a file nor a directory")
        _format = {'src': src, 'dst': dst, 'mode':mode}
        return return_format.format(**_format)
    except OSError as e:
        raise OSError(f"Error copying file from {src} to {dst}: {e}") from e

class Path:
    def __init__(self, path: str):
        self.path = path
        self.exist = exists(path)
    @property
    def abspath(self):
        return abspath(self.path)
    @property
    def dir(self):
        return path_split(self.path)[0]
    @property
    def file(self):
        return path_split(self.path)[-1]
    def __str__(self):
        return self.path
    def get(self, *path):
        return join(self.path, *path)
    
    @property
    def type(self) -> Optional[Literal['dir', 'file']]:
        src = self.path
        if isdir(src):
            return 'dir'
        elif isfile(src):
            return 'file'
        else:
            return None

    
def get_data_path(dir_name:str, copy_dir_or_file:list = [], root_dir:str = None) -> Path:
    """
    Return the path to the directory for storing application data, or a tuple of a boolean and the path.
    
    >>> exists,program_data_path = get_data_path('Intel')

    :param dir_name: The name of the directory to create.
    :param copy_dir_or_file: A list of files/directories to copy into the created directory.
    :param replace: Whether to replace the directory if it already exists.
    :return: A tuple of a boolean and the path to the created directory.If the directory already existed, the boolean will be True.

    """
    def _mkDir(): 
        for dir_or_file in copy_dir_or_file: 
            _n = join(program_data_path, dir_or_file)
            if not exists(_n):  mkdir(_n)
    program_data_path = join(environ.get('ProgramData', '/var/lib'), dir_name)
    no_exists = not isdir(program_data_path)
    _mkDir()
    if no_exists:
        mkdir(program_data_path)
        for dir_or_file in copy_dir_or_file:
            dir_or_file = join(root_dir, dir_or_file) if root_dir else dir_or_file
            copy(dir_or_file, program_data_path)
        _p = Path(program_data_path)
        _p.exist = False
        return _p
    else:
        _p = Path(program_data_path)
        _p.exist = True
        return _p
    
class base64:
    """
    Base64 encoding and decoding.

    ## Example
    >>> value_str = 'abcde'
    >>> value_list = ['ac','cd']
    >>> b64_str = base64(value_str).encode()
    >>> b64_list = base64(value_list).encode()
    >>> b64_str
    'YWJjZGU%3D'
    >>> b64_list
    'YWMsY2Q%3D'
    >>> base64(b64_str).decode()
    'abcde'
    >>> base64(b64_list).decode()
    ['ac', 'cd']
    """
    # __slots__ = ("data",)

    def __init__(self, data: Union[str,list]) -> None:
        self.data = str(','.join(data))  if isinstance(data, list) else str(data)

    def encode(self) -> str:
        """Encode the stored data to a base64 string."""
        b64 = b64encode(self.data.encode()).decode("utf-8")
        return quote(b64)

    def decode(self) -> Union[str, list[str]]:
        """
        Decode the stored base64 string to the original string.

        Returns a list of strings if the original data was a list, otherwise a single string.
        """
        decoded_string = b64decode(unquote(self.data)).decode()
        return decoded_string.split(",") if "," in decoded_string else decoded_string

def convert_size(size_bytes):
    """
    >>> convert_size(1024)
    '1.0 KB'
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"  

def errorCallback(errorCallback:Optional[Callable[[str],Any]]=None, *errorCallbackArgs, **errorCallbackKwargs):
    def decorator(func:Callable):
        def wrap(*args, **kwargs):
            try:
                return func(*args, **kwargs)   # print(func.__name__)
            except Exception as e:
                if errorCallback:
                    errorCallback(e, *errorCallbackArgs, **errorCallbackKwargs)
                else:
                    print(e)
        return wrap
    return decorator

if __name__ == '__main__':
    import doctest
    print(doctest.testmod())