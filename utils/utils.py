from datetime import timedelta,datetime,timedelta
from shutil import copy2
from base64 import b64encode,b64decode
from typing import Any, Union
import math
from hashlib import sha3_256
from json import load, dump
def hash(text:str) -> str:
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

    def __call__(self, key:str, value = None) -> Any:
        keys = key.split('/')
        if value: 
            result = self._set(keys, value)
            self.dump(result)
            return result
        else:
            return self._get(keys)

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
def read_card_data() -> str:
    """
    Reads card data from the card reader.
    """
    input("請刷卡...")
    return input()

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
    ```
    msg=msgw('title','contant',0,1000)  # time (ms)
    print(msg)
    ```
    """
    import ctypes
    # MessageBoxTimeoutW(父窗口句柄,消息內容,標題,按鈕,語言ID,等待時間)
    return ctypes.windll.user32.MessageBoxTimeoutW(0, text, title, style,0,time)

def now_time() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def copy_file(dst: str, src: str = './writable/home.db') -> None:
    """
    Copies a file from the `src` path to the `dst` path.

    :param src: The source file path. Must be a Path object.
    :param dst: The destination file path. Must be a Path object.
    :return: None
    """
    if not src or not dst:
        raise ValueError("Both src and dst must be non-empty")
    try:
        copy2(src, dst)
    except OSError as e:
        raise OSError(f"Error copying file from {src} to {dst}: {e}") from e

class base64:
    """
    Base64 encoding and decoding.

    ## Example

    ```
    value_str = 'abcde'
    value_list = ['ac','cd']
    b64_str = base64(value_str).encode()
    b64_list = base64(value_list).encode()

    print(b64_str)      # YWJjZGU=
    print(b64_list)     # YWMsY2Q=
    print(base64(b64_str).decode())     # abcde
    print(base64(b64_list).decode())    # ['ac', 'cd']
    ```
    """
    # __slots__ = ("data",)

    def __init__(self, data: Union[str,list]) -> None:
        self.data = str(','.join(data))  if isinstance(data, list) else str(data)

    def encode(self) -> str:
        """Encode the stored data to a base64 string."""
        return b64encode(self.data.encode()).decode("utf-8")
    def decode(self) -> Union[str, list[str]]:
        """
        Decode the stored base64 string to the original string.

        Returns a list of strings if the original data was a list, otherwise a single string.
        """
        decoded_string = b64decode(self.data).decode()
        return decoded_string.split(",") if "," in decoded_string else decoded_string
        
def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"