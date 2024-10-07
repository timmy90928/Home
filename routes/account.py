
from . import Blueprint, render_template, request, redirect, url_for, db, User, jsonify, app
from . import login_user, logout_user, login_required, current_user
from utils.utils import hash

account_bp = Blueprint('account', __name__, url_prefix='/account')
HEADS = ['流水號', '帳號', '名稱', '權限']
HEADS_SQL = "id,username,name,role"

@account_bp.route('/')
@login_required
def index():
    if current_user.rolenum > 0:  return render_template('common/list.html', title = "權限錯誤", heads = ['此頁面僅提供給管理員使用'])
    return render_template('account/manager.html', datas = db.get_col('account', HEADS_SQL), heads = HEADS)

@account_bp.route('/edit/<id>', methods=['GET', 'POST'])
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
    return render_template('account/login.html', title = "個人帳號管裡", datas = db.get_row('account', ['id', id],HEADS_SQL)[0])

@account_bp.route('/database/add', methods=['POST'])
def add():
    username = request.json['username']
    print(username)
    db.add('account', {'username':username, 'name':username, 'password':hash(username)})
    return jsonify({'data': username}) # redirect('/account')
@account_bp.route('/database/delete/<id>', methods=['GET'])
def delete(id):
    if db.get_row('account', ['id', id],'role')[0][0] in ('admin', 'developer'):  return redirect('/alert/此帳號無法刪除')
    db.delete('account', ['id', id])
    return redirect('/account')
@account_bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if password == app.secret_key: 
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
    return render_template('account/login.html', title = "登入")
@account_bp.route('/logout')
def logout():
    logout_user()
    return redirect('/')