from . import (app, Blueprint, render_template, request, redirect, clients, send_from_directory, url_for, 
               timestamp, now_time, listdir, path, stat, remove)
from . import login_user, logout_user, login_required, current_user
from platform import system,node
from utils.web import get_latest_release, check_file
from utils.utils import copy_file, convert_size

server_bp = Blueprint('server', __name__, url_prefix='/server')

@server_bp.route('/')
def index():
    return redirect('/server/info')

@server_bp.route('/info', methods=['GET'])
# @login_required
def info():
    try: 
        latest_version, latest_download_url, updated = get_latest_release(app.config['TITLE'])
    except:
        latest_version, latest_download_url, updated = '無法取得最新版本資訊', '#', '無法取得最新版本資訊'
    data = [
        ['伺服器名稱', node()],
        ['伺服器系統', system()], 
        ['伺服器版本', app.config['VERSION']],
        ['伺服器啟動時間', app.config['SERVER_RUN_TIME']],
        ['目前連線數',len(clients)],
        ['目前連線IP', str('、'.join(clients))],
        ['最新版本', f'<a href="{latest_download_url}">{latest_version}</a>  (更新時間: {updated})']
    ]
    return render_template('common/list.html', title='伺服器資訊',heads=['Key','Value'],datas=data)

@server_bp.route('/cloud', methods=['GET'])
@login_required
def cloud():
    data = []
    files = listdir(app.config['UPLOAD_FOLDER'])
    def time_convert(ts ):return timestamp(ts=ts)
    for file in files:
        file_info = stat(path.join(app.config['UPLOAD_FOLDER'], file))
        data.append([file,convert_size(file_info.st_size),time_convert(file_info.st_atime),time_convert(file_info.st_mtime),time_convert(file_info.st_ctime)]) # 檔案名稱、檔案大小、上次存取時間、上次修改時間、建立時間
    return render_template('server/cloud.html', files=data)

@server_bp.route('/cloud/upload', methods=['POST'])
def upload():
    """
    Handles an upload request by saving the file to the configured upload folder.
    """
    try: file = check_file(request)
    except AssertionError as e: return str(e), 500
    if file.filename == 'home.db':
        copy_file(f'./writable/home_{now_time().replace("-","_").replace(" ","_").replace(":","_")}.db')
    file.save(path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return redirect('/server/cloud')

@server_bp.route("/cloud/download/<path:filename>")
def download(filename: str):
    """Handles a download request by sending the file from the configured upload folder."""
    try:
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404

@server_bp.route("/cloud/delete/<filename>")
def delete(filename: str):
    """Handles a delete request by removing the specified file from the upload folder."""
    file_path = path.join(app.config["UPLOAD_FOLDER"], filename)
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