from . import *
from utils.g import current_user, current

root_bp = Blueprint('root', __name__)

@root_bp.route('/', methods=['GET'])
def index():
    _p = current.config.get('blog/path')
    
    if _p:
        path = Path(_p)
        directories = [item.name for item in path.iterdir() if item.is_dir()]
        numeric_data = [int(item) for item in directories if item.isdigit()]

        year = request.args.get('year', max(numeric_data))
        path_year = Path(_p).joinpath(f'{year}')
        directories = [item for item in path_year.iterdir()]

        datas = []
        for directory in directories:
            try:
                blog_cfg = json(str(directory.joinpath('config.json')), create=False)
            except:
                blog_cfg = {}

            blog_cfg['path_name'] = directory.name
            blog_cfg['title'] = blog_cfg.get('title', directory.name.split(' ')[1])
            blog_cfg['date'] = blog_cfg.get('date', directory.name.split(' ')[0])
            blog_cfg['folder'] = blog_cfg.get('folder', 'favorite')
            blog_cfg['path'] = str(directory.joinpath(blog_cfg['folder']) if directory.joinpath(blog_cfg['folder']).is_dir() else directory)
            blog_cfg['token'] = token.generate({'year': year, 'name': blog_cfg['path_name'], 'path': blog_cfg['path']})
            blog_cfg['logo'] = blog_cfg.get('logo', current.config.get('blog/logo',"logo.JPG"))
            blog_cfg['text'] = blog_cfg.get('text', '')

            datas.append(blog_cfg)
    else:
        abort(500, response=gettext("Blog path not set."))
    
    return render_template('index.html', max_year=max(numeric_data), min_year=min(numeric_data), datas=datas, year=year)

@root_bp.route('/blog/<cfg_token>', methods=['GET'])
def blog_place(cfg_token):
    tkn:dict[str, str] = token.verify(cfg_token)
    year = tkn['year']
    name = tkn['name']
    _p = Path(tkn['path'])

    img_index = int(request.args.get('index',-1))
    imgs = [_ for _ in _p.iterdir() if _.suffix[1:].lower() in ('jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'avif', 'tiff')]

    return render_template('travel/blog.html',name=name, img_index=img_index, imgs=imgs, year=year, now=cfg_token)

@root_bp.route('/home', methods=['GET'])
@login_required
def home():
    return render_template('home.html',dev = True if current_user.rolenum == 0 else False)

@root_bp.route('/show/<path:filepath>')
def show_image(filepath):
    #? User Headshot: /show/headshot/headshot_user_1?folder=upload&iferror=person-circle.svg
    errorfile = Path("static/picture").joinpath(request.args.get('iferror', 'file-x-3-2.svg')).absolute()
    path = Path(filepath)
    if "headshot_user" in path.name:
        login_required_role.onlyself(path.name.split('_')[-1].split('.')[0])

    with SkipError():
        folder = Path(current.config.get(f"folder/{request.args.get('folder')}"))
        path = folder / path

    path = path.get_all_suffix(only_one=True)
    if path and path.exists(): 
        return send_file(str(path), last_modified=path.stat().st_mtime, max_age=60)
    else:
        return send_file(errorfile, max_age=60*60)

@root_bp.route("/db", methods=['GET'])
@login_required_role.developer
def db_index():
    datas = []
    for table in current.db.get_table():
        datas.append([f'<a href="/db/{table}">{table}</a>'])
    return render_template('common/list.html',title='資料表',datas=datas, heads=['資料表名稱'])

@root_bp.route("/db/<table_name>", methods=['GET'])
@login_required_role.developer
def show(table_name):
    return render_template('common/list.html',title=table_name,datas=current.db.get_col(table_name,'*'),heads=current.db.get_head(table_name))

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
    return send_file(Path('./static').joinpath(filename))

@root_bp.route('/cause/<int:status_code>', methods=['GET'])
def cause(status_code:int):
    abort(status_code, response="此為測試用")

@root_bp.route('/setlang', methods=['GET', 'POST'])
def setlang():
    session['lang'] = request.form.get('lang')
    path = request.referrer
    return redirect(path)

@root_bp.route('/setmobile/<mobile>', methods=['GET'])
def setmobile(mobile:str):
    mobile = True if mobile.lower() == 'true' else False
    session['mobile'] = bool(mobile)
    path = request.referrer
    return redirect(path)

@root_bp.route('/input', methods=['GET', 'POST'])
def data_input():
    data:dict = Token().verify(request.args.get('token'),10)
    return render_template('common/input.html', title = data['title'], datas = data['datas'], args = data['args'], action =  data['action'])

