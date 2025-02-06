
from . import (current_app, Blueprint, render_template, request, redirect,  send_from_directory, url_for, 
               timestamp, now_time, listdir, path, stat, remove, abort)
from . import login_user, logout_user, login_required

from utils.g import current_user, current, User
from platform import system,node
from utils.web import errorCallback
from utils.utils import copy, convert_size, base64
from os.path import isfile, isdir, split,  join, exists, dirname
from os import listdir, stat, getcwd, environ, rmdir, mkdir, removedirs
import shutil
from flask import send_file
import mimetypes

tcloud_bp = Blueprint('tcloud', __name__, url_prefix='/tcloud')
db = current.db

@tcloud_bp.route("/", methods=['GET'])
def tcloud_root():
    return redirect('/tcloud/root')


@tcloud_bp.route("/<path:path>", methods=['GET'])
def tcloud(path):
    root = current_app.config['tcloud']
    path = '.' if path=='root' else path
    abspath = join(root,path)
    if isfile(abspath):
        mime_type = mimetypes.guess_type(path)[0]
        return send_file(abspath, mimetype=mime_type if mime_type else 'text/plain') # , mimetype=mime_type), 200 if mime_type else send_from_directory(root,path), 200
      
    elif isdir(abspath) or path=='root':
        dirlists, filelists = [], []
        for _ in listdir(abspath):
            if isfile(join(abspath,_)):
                filelists.append([_,f"<a href='/tcloud/{join(path,_)}'>{_}</a>", convert_size(stat(join(abspath,_)).st_size), timestamp(ts=stat(join(abspath,_)).st_atime), timestamp(ts=stat(join(abspath,_)).st_mtime), timestamp(ts=stat(join(abspath,_)).st_ctime)])
            else:
                dirlists.append([_,f"<a href='/tcloud/{join(path,_)}'>{_}</a>", timestamp(ts=stat(join(abspath,_)).st_atime), timestamp(ts=stat(join(abspath,_)).st_mtime), timestamp(ts=stat(join(abspath,_)).st_ctime)])
    else:
        abort(404, response='資料夾或檔案不存在')

    return render_template('server/tcloud.html', filelists=filelists, dirlists=dirlists, now_path='root' if path=='.' else path), 200

@tcloud_bp.route("/ppage", methods=['GET'])
def ppage():
    path = request.args.get('path')
    path = path.split('/')[:-1]
    path = '/'.join(path)
    return redirect(f'/tcloud/{path}')

@tcloud_bp.route('/upload', methods=['POST'])
def tcloud_upload():
    """
    Handles an upload request by saving the file to the configured upload folder.
    """
    path = request.args.get('path','root')
    if 'file[]' not in request.files:
        raise AssertionError('No file part')
    files = request.files.getlist('file[]')
    if files[0].filename == '':
        return redirect("/alert/請選擇檔案")
    for file in files:
        abspath = join(current_app.config['tcloud'],"" if path=='root' else path, file.filename)
        file.save(abspath)
    return redirect(f"/tcloud/{path}")

@tcloud_bp.route('/mkdir', methods=['POST'])
def make_dir():
    """
    Handles an upload request by saving the file to the configured upload folder.
    """
    newdir = request.form.get('dirname')
    path = request.args.get('path','root')
    path = join(current_app.config['tcloud'], path, newdir)
    mkdir(path)
    return redirect(f"/tcloud/{path}")

@tcloud_bp.route("/download/<path:filename>")
@errorCallback(note='下載失敗')
def tcloud_download(filename: str):
    """Handles a download request by sending the file from the configured upload folder."""
    filepath = join(current_app.config["tcloud"], filename)
    try:
        if isfile(filepath):
            #print(filename)
            return send_from_directory(current_app.config["tcloud"], filename, as_attachment=True)
        else:
            if not exists(filepath): abort(404, response='資料夾或檔案不存在')
            zip_file = zip_folder(filepath)
            zip_files = split(zip_file)
            return  send_from_directory(zip_files[0], zip_files[1], as_attachment=True)
    except FileNotFoundError as e:
        abort(404, response=str(e))

@tcloud_bp.route("/delete/<path:filename>")
@login_required
@errorCallback(note='刪除失敗')
def tcloud_delete(filename: str):
    """Handles a delete request by removing the specified file from the upload folder."""
    if current_user.rolenum > 2:  return redirect('/error/role/2')
    file_path = path.join(current_app.config["tcloud"], filename)

    if path.isfile(file_path):
        try:
            remove(file_path)
            return redirect(f'/tcloud/{split(filename)[0]}')
        except Exception as e:
            return str(e), 500
    elif path.isdir(file_path):
        try:
            removedirs(file_path)
            return redirect(f'/tcloud/{split(filename)[0]}')
        except Exception as e:
            return str(e), 500
    else:
        return "File not found", 404
    

@errorCallback(note='壓縮失敗')
def zip_folder(folder_path):
    zip_filename = join(environ.get('temp','/tmp'), "tcloud")
    shutil.make_archive(zip_filename, 'zip', folder_path)
    return zip_filename+'.zip'