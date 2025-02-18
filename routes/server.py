from . import *
from platform import system,node
from utils.web import get_latest_release, check_file, download_file
from utils.utils import copy, convert_size, base64
from utils.g import clients, current_user

server_bp = Blueprint('server', __name__, url_prefix='/server')

@server_bp.route('/')
def index():
    return redirect('/server/info')

@server_bp.route('/info', methods=['GET'])
@login_required
def info():
    try: 
        latest_version,web,[latest_download_url, size, updated] = get_latest_release(current_app.config['TITLE'])
    except:
        latest_version, latest_download_url, updated = '無法取得最新版本資訊', '#', '無法取得最新版本資訊'
    data = [
        ['伺服器名稱', node()],
        ['伺服器系統', system()], 
        ['伺服器版本', current_app.config['VERSION']],
        ['伺服器啟動時間', current_app.config['SERVER_RUN_TIME']],
        ['目前連線數',len(clients)],
        ['目前連線IP', str('、'.join(clients))],
        ['最新版本', f'<a href="{web}">{latest_version}</a>  (更新時間: {updated}'],
    ]
    return render_template('common/list.html', title='伺服器資訊',heads=['Key','Value'],datas=data)

FILE_HEAD = ["檔案名稱", "檔案大小", "上次存取時間", "上次修改時間", "建立時間", "下載", "刪除"]
@server_bp.route('/cloud', methods=['GET'])
@login_required
def cloud():
    data = []
    files = listdir(current_app.config['UPLOAD_FOLDER'])
    def _ts(ts ):return timestamp(ts=ts)
    for file in files:
        file_info = stat(path.join(current_app.config['UPLOAD_FOLDER'], file))
        data.append([file,convert_size(file_info.st_size),_ts(file_info.st_atime),_ts(file_info.st_mtime),_ts(file_info.st_ctime)]) # 檔案名稱、檔案大小、上次存取時間、上次修改時間、建立時間
    datas = [add_small_button(*_, blue=['下載',f'/server/cloud/download/{_[0]}'], red=[f'確定要刪除 {_[0]} 嗎',f'/server/cloud/delete/{_[0]}' ]) for _ in data]
    return render_template('server/cloud.html', files=datas, heads=FILE_HEAD)

@server_bp.route('/cloud/upload', methods=['POST'])
@login_required_role.user
def upload():
    """
    Handles an upload request by saving the file to the configured upload folder.
    """
    try: file = check_file(request)
    except AssertionError as e: return str(e), 500
    if file.filename == 'home.db':
        copy('./writable/home.db',f'./writable/home_{now_time().replace("-","_").replace(" ","_").replace(":","_")}.db')
    file.save(path.join(current_app.config['UPLOAD_FOLDER'], file.filename))
    return redirect('/server/cloud')

@server_bp.route("/cloud/download/<path:filename>")
@login_required
def download(filename: str):
    """Handles a download request by sending the file from the configured upload folder."""
    try:
        return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404

@server_bp.route("/cloud/delete/<filename>")
@login_required_role.user
def delete(filename: str):
    """Handles a delete request by removing the specified file from the upload folder."""
    file_path = path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if filename in ('home.db', 'config.json'):
        return redirect('/alert/無法刪除預設檔案')
    if path.isfile(file_path):
        try:
            remove(file_path)
            return redirect('/server/cloud')
        except Exception as e:
            return str(e), 500
    else:
        return "File not found", 404

import json
@server_bp.route("/setting", methods=['GET', 'POST'])
@login_required_role.admin
def settings():
    if request.method == 'POST':
        data = request.form
        
        _to = data['_to']
        if _to == 'delete':
            current.config.delete(data['_from'])
        else:
            match _to:
                case '':        _to = "'null'"
                case 'null':    _to = "'null'"
                case 'true':    _to = "'True'"
                case 'false':   _to = "'False'"
            print(f"current.config(data['_from'], {_to})")
            exec(f"current.config(data['_from'], {_to})")
        return redirect('/server/setting')

    data = current.config.load()
    return render_template('server/setting.html', cfg=json.dumps(data, ensure_ascii=False, indent=8))