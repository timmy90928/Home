from . import Blueprint, render_template, request, db, jsonify,listdir, app, send_from_directory, redirect, abort
from . import login_user, logout_user, login_required, current_user

root_bp = Blueprint('root', __name__)

@root_bp.route('/', methods=['GET'])
def index():
    files = listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html',datas=files, dirs=app.config['UPLOAD_FOLDER'])

@root_bp.route('/home', methods=['GET'])
@login_required
def home():
    return render_template('home.html',dev = True if current_user.rolenum == 0 else False)

@app.route('/writable/<path:filename>')
def send_image(filename):
    return send_from_directory('writable', filename)

@root_bp.route("/db", methods=['GET'])
@login_required
def db_index():
    if current_user.rolenum > 0:  return abort(401, response="此頁面僅提供給開發者使用")
    datas = []
    for table in db.get_table():
        datas.append([f'<a href="/db/{table}">{table}</a>'])
    return render_template('common/list.html',title='資料表',datas=datas, heads=['資料表名稱'])

@root_bp.route("/db/<table_name>", methods=['GET'])
@login_required
def show(table_name):
    if current_user.rolenum > 0:  return redirect('/error/role/0')
    return render_template('common/list.html',title=table_name,datas=db.get_col(table_name,'*'),heads=db.get_head(table_name))

@root_bp.route('/error/role/<message>', methods=['GET'])
def role_error(message: str):
    """```
    if current_user.rolenum > 0:  return redirect('/error/role/0')
    ```"""
    match message:
        case '0': message = '此頁面僅提供給開發者使用'
        case '1': message = '此頁面僅提供給管理員使用'
        case '2': message = '此頁面僅提供給一般使用者與管理員使用'
    return render_template('common/list.html', title = "權限錯誤", heads = [message])

@root_bp.route('/alert/<message>', methods=['GET'])
def alert(message: str) -> None:
    """Prints an alert message to the terminal."""
    to = request.args.get('to',None)
    return render_template('common/alert.html', message=message, url=to)

@root_bp.route('/confirm/<message>', methods=['GET'])
def confirm(message: str) -> None:
    """/confirm/test?to=/"""
    to = request.args.get('to',None)
    return render_template('common/confirm.html', message=message+'?', url=to)

@root_bp.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        data = request.json
        response = {'message': 'Received!', 'data': data}
        return jsonify(response)
    return render_template('test/fetch.html')

@root_bp.route('/.well-known/pki-validation/<filename>')
def serve_validation_file(filename):
    """
    For use with [ZeroSSL] verified domains.

    [ZeroSSL]: https://manage.sslforfree.com/dashboard "SSL for Free"
    """
    return send_from_directory('./static', filename)

@root_bp.route('/cause/<int:status_code>', methods=['GET'])
def cause(status_code:int):
    abort(status_code, response="此為測試用")