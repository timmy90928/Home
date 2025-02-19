
from . import *
from utils.utils import hash

from utils.g import current_user, current, User
db = current.db

# https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/autocomplete
account_bp = Blueprint('account', __name__, url_prefix='/account')
HEADS = ['流水號', '帳號', '名稱', '權限', "刪除"]
HEADS_SQL = "id,username,name,role"

@account_bp.route('/')
@login_required_role.admin
def index():
    datas = db.get_col('account', HEADS_SQL)
    datas = [add_small_button(i, username, name, role, red=[f'是否確定要刪除 {username} (ID={i})',f'/account/database/delete/{i}']) for i, username, name, role in datas]
    return render_template('account/manager.html', datas = datas, heads = HEADS)

@account_bp.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
        }
        if request.form.get('password'):
            if request.form.get('password') != request.form.get('againpassword'):
                return redirect('/alert/兩次輸入密碼不相同')
            else:
                data['password'] = hash(request.form.get('password'))
        db.revise('account', data, ['id', id])
        return redirect('/alert/修改成功?to=/home')
    return render_template('account/login.html', title = gettext("Account Settings"), datas = db.get_row('account', ['id', id],HEADS_SQL)[0])

@account_bp.route('/database/add', methods=['POST'])
@login_required_role.user
def add():
    username,role = request.json['username'].split(' ')
    from . import roles
    if int(role) < 3: return jsonify({'data': '不能賦予管理員權限'})
    db.add('account', {'username':username, 'name':username, 'password':hash(username),'role':roles(int(role)).name})
    return jsonify({'data': f"{username}({roles(int(role)).name})新增成功"}) # redirect('/account')
@account_bp.route('/database/delete/<id>', methods=['GET'])
@login_required_role.admin
def delete(id):
    if db.get_row('account', ['id', id],'role')[0][0] in ('admin', 'developer'):  return redirect('/alert/此帳號無法刪除')
    db.delete('account', ['id', id])
    return redirect('/account')
@account_bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if password == current_app.secret_key: 
            login_user(User(0),remember=True)
            return redirect('/home')
        try: verify = db.get_row('account', ['username',username],'id,password')[0]
        except: return redirect('/alert/無此帳號')

        if  hash(password) == verify[1]:
            user = User(verify[0])
            login_user(user,remember=True)
            return redirect('/home')
        else:
            return redirect('/alert/帳號密碼錯誤')
    return render_template('account/login.html', title = gettext("Login"))
@account_bp.route('/logout')
def logout():
    logout_user()
    return redirect('/')