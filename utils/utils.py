from datetime import timedelta,datetime,timedelta
from shutil import copy2, rmtree, ignore_patterns, copytree
from os import environ,mkdir, name as osname
from os.path import isfile, isdir, split as path_split,join, abspath, exists, getctime
from base64 import b64encode,b64decode
from urllib.parse import quote, unquote
from typing import Any, Union, Optional, Callable
import math
from hashlib import sha3_256
from pathlib import WindowsPath, PosixPath, Path as _Path
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
    def __init__(self, path:str, create:bool = True) -> None:
        self.path = Path(path)
        
        if not self.path.exists():
            if create:
                self.path.touch()
                self.dump({})
            else:
                raise FileNotFoundError(f"JSON file '{path}' does not exist.")

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
        if value is not None: 
            if value == "null": value = None
            if value in ["True", "true"]: value = True
            if value in ["False", "false"]: value = False
            result = self._set(keys, value)
            self.dump(result)
            return result
        else:
            return self._get(keys)
    def __getitem__(self, key):
        return self.__call__(key, value = None)
    def __setitem__(self, key, value):
        return self.__call__(key, value)
    
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
        for i, k in enumerate(keys):
            if k == '': continue
            _ += f"['{k}']"

            if i == len(keys) - 1:
                exec(f"{_} = value")
            else:
                if k not in temp:
                    exec(f"{_} = {{}}")

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

    def delete(self, key:str) -> bool:
        keys = key.split('/')
        data = self.load()
        
        # Traversing through the keys
        temp = data
        for k in keys[:-1]:  # Get to the parent of the key to delete
            if k in temp:
                temp = temp[k]
            else:
                return False  # If the key doesn't exist, return False
        
        # Deleting the key
        if keys[-1] in temp:
            del temp[keys[-1]]
            self.dump(data)  # Save the updated data back to the file
            return True
        else:
            return False
        
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

#// https://stackoverflow.com/questions/61689391/error-with-simple-subclassing-of-pathlib-path-no-flavour-attribute
class Path(type(_Path()), _Path):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)
    
    def __init__(self, path: str):
        self.path = path
        self.exist = exists(path)

    def not_exist_create(self, create_file:bool = True):
        if self.suffix:
            self.parent.mkdir(parents=True, exist_ok=True)
            if create_file: self.touch(exist_ok=True)
        else:  # No file extension, treated as a directory.
            self.mkdir(parents=True, exist_ok=True)
        return not self.exist
    
    @overload
    def get_all_suffix(self) -> Optional[list[_Path]]: ...
    @overload   
    def get_all_suffix(self, only_one:bool = False) -> Optional[_Path]: ...
    def get_all_suffix(self, only_one:bool = False):
        if not self.suffix:
            paths = list(self.parent.glob(f"{self.name}.*"))
            match len(paths):
                case 0:
                    return None
                case 1:
                    return paths[0]
                case _:
                    return paths[0] if only_one else paths
        else:
            return self

    def del_all_suffix(self):
        if not self.suffix:
            paths = list(self.parent.glob(f"{self.name}.*"))
            for path in paths:
                path.unlink()
        else:
            self.unlink()

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
    
    >>> p = get_data_path('Intel')
    >>> p.exist
    True
    >>> p.type
    'dir'

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
        return Path(program_data_path)
    else:
        return Path(program_data_path)
    
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

def list2str(_list:list):
    """
    >>> list2str([1,2,3])
    '1,2,3'
    """
    return ",".join([str(i) for i in _list])

def none2precent(obj:object):
    """
    The original object if it is truthy, otherwise "%".

    Examples:
        >>> none2precent(5)
        5
        >>> none2precent(0)
        '%'
        >>> none2precent(None)
        '%'
    """
    return obj if obj else "%"

def ifelse(_if:object, _else:object):
    """
    If _if is truthy, return _if; otherwise, return _else.

    Examples:
        >>> ifelse(1, 0)
        1
        >>> ifelse(0, 1)
        1
        >>> ifelse('', 'foo')
        'foo'
        >>> ifelse('bar', '')
        'bar'
    """
    return _if if _if else _else

def manage_file_count(dst_folder:Union[str,Path], pattern:str, keep_latest:int = 3, src:str = None) -> bool:
    """
    Manage the number of archives and only keep the latest specified number.

    :param dst_folder: The path to the target archives.
    :param pattern: Patterns matching archives, E.g., 'home_backup_{time}.db'。
    :param keep_latest: Latest quantity to keep.
    :param src: Source file path.
    """
    if isinstance(dst_folder, str): dst_folder = Path(dst_folder)

    if src:
        backup_path = dst_folder.joinpath(pattern.format(time=now_time("%Y_%m%d_%H_%M_%S")))
        copy2(src, backup_path)

    # Confirm that the target directory exists.
    if not dst_folder.exists():
        raise FileNotFoundError(f"The destination directory ({dst_folder}) does not exist.")

    # Get all files matching the pattern.
    backup_files = sorted(dst_folder.glob(pattern.format(time="*")), key=getctime)
    
    # If the file exceeds the limit, delete the oldest file.
    if len(backup_files) > keep_latest:
        for old_backup in backup_files[:-(keep_latest+1)]:
            old_backup.unlink()
        return True
    else:
        return False

if __name__ == '__main__':
    import doctest
    print(doctest.testmod())