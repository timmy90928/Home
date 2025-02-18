from . import *
from utils.db import IE_TOTAL_SQL
from utils.g import current_user, current

accounting_bp = Blueprint('accounting', __name__, url_prefix='/accounting')
db = current.db
HEADS = ['流水號','日期','收支','類別','細項','金額','備註', '編輯','刪除']
HEADS_SQL = "id,strftime('%Y-%m-%d', Datestamp, 'unixepoch','localtime'),ie,Category,Detail,Amount,note"

@accounting_bp.route('/add', methods=['GET'])
@login_required_role.user
def add():
    if current_user.rolenum > 2:  return redirect('/error/role/2')
    notelist = current.db.get_col('Accounting', 'note', distinct=True)
    return render_template('accounting/add.html', notelist=notelist)

@accounting_bp.route('/<year>/<month>', methods=['GET'])
@login_required
def monthly_analysis(year, month):
    # https://github.com/timmy90928/Home/issues/2
    e  = analysis(year, month, '支出')
    i  = analysis(year, month, '收入')
    e_values = list(e.values())
    i_values = list(i.values())
    datas = db(f"SELECT {HEADS_SQL} FROM Accounting WHERE Datestamp BETWEEN {timestamp(year,month)} AND {timestamp(year,int(month)+1,dsecond=-1)} ORDER BY Datestamp DESC")
    datas = [add_small_button(*_, blue=['編輯',f'/accounting/edit/data/{_[0]}'], red=[gettext("Do you want to delete %(name)s (ID=%(id)s)?", id=_[0], name=_[4]),f'/accounting/database/delete/{_[0]}' ]) for _ in datas]
    return render_template('accounting/search.html',title='月分析',month = f'{year}-{month}',t_datas = [[i_values[-1],e_values[-1],int(i_values[-1])-int(e_values[-1])]],
                           datas = datas, heads = HEADS,
                           e_datas = [e_values], e_heads = list(e.keys()),
                           i_datas = [i_values], i_heads = list(i.keys()))

@accounting_bp.route('/analysis/month', methods=['GET','POST'])
@login_required
def month_analysis():
    if request.method == 'POST':
        date = request.form.get('Date')
        date = date.split('-')
    else:
        date = now_time().split(' ')[0].split('-')
    return redirect(f'/accounting/{date[0]}/{date[1]}')

@accounting_bp.route('/search', methods=['GET','POST'])
@login_required
def search():
    if request.method == 'POST':
        form = request.form
        startDate = form.get('startDate') if form.get('startDate') else '%'
        endDate =   form.get('endDate') if form.get('startDate') else '%' # datetime.strptime(form.get('endDate'), "%Y-%m-%d").timestamp()
        minAmount= form.get('minAmount') if form.get('minAmount') else int(0)
        maxAmount = form.get('maxAmount') if form.get('maxAmount') else 'Infinity'
        data = {
            'ie': form.get('ie') if form.get('ie') else '%',
            'Category': form.get('Category') if form.get('Category') else '%',
            'Detail': form.get('Detail') if form.get('Detail') else '%',
            'note': f"%{form.get('note')}%" if form.get('note') else '%'
        }

        date = f"AND Datestamp BETWEEN strftime('%s', '{startDate}') AND strftime('%s', '{endDate}')" if form.get('startDate') and form.get('endDate') else ''
        datas = db.get_col('Accounting', HEADS_SQL, data, 
                           customize= f"{date} AND Amount BETWEEN '{minAmount}' AND '{maxAmount}' ORDER BY Datestamp DESC")
        
        data['ie'] = '收入'
        sum_i = db.get_col('Accounting','sum(Amount)', data, 
                           customize= f" {date} AND Amount BETWEEN '{minAmount}' AND '{maxAmount}' ORDER BY Datestamp DESC")[0][0]
        sum_i = sum_i if sum_i else 0
        data['ie'] = '支出'
        sum_e = db.get_col('Accounting','sum(Amount)', data, 
                           customize= f" {date} AND Amount BETWEEN '{minAmount}' AND '{maxAmount}' ORDER BY Datestamp DESC")[0][0]
        sum_e = sum_e if sum_e else 0
        
        sum_total = int(sum_i) - int(sum_e)

        datas = [add_small_button(*_, blue=['編輯',f'/accounting/edit/data/{_[0]}'], red=[gettext("Do you want to delete %(name)s (ID=%(id)s)?", id=_[0], name=_[4]),f'/accounting/database/delete/{_[0]}' ]) for _ in datas]
        return render_template('accounting/search.html',title='搜尋', datas=datas, heads=HEADS, t_datas = [[sum_i,sum_e,sum_total]])

    return render_template('accounting/search.html',title='搜尋')

@accounting_bp.route('/edit/data/<id>', methods=['GET'])
@login_required_role.user
def editdata(id):
    datas = db.get_row('Accounting', ['id', id],HEADS_SQL)[0] # note
    return render_template('accounting/add.html',datas=datas)

@accounting_bp.route('/getCategories', methods=['POST'])
@login_required
def getCategories():
    data = request.json  # Get the JSON data in the request.
    ie = data['ie']
    Category = current.config(f'ie_class/{ie}')
    response = {'message': 'Received!', 'categories': Category}
    return jsonify(response)

@accounting_bp.route('/database/add', methods=['POST'])
@login_required_role.user
def data_add():
    form = request.form
    data = {
        'Datestamp': timestamp(string=form.get('Date')),
        'ie': form.get('ie'),
        'Category': form.get('Category'),
        'Detail':  form.get('Detail'),
        'Amount': form.get('Amount'),
        'Creatdate': now_time(),#"datetime('now','localtime')"
        'note': form.get('note')
    }
    db.add('Accounting', data)
    return redirect(f'/alert/於{now_time()}新增成功?to=/accounting/add')

@accounting_bp.route('/database/revise/<id>', methods=['POST'])
@login_required_role.user
def data_revise(id):
    form = request.form
    data = {
        'Datestamp': timestamp(string=form.get('Date')),
        'ie': form.get('ie'),
        'Category': form.get('Category'),
        'Detail':  form.get('Detail'),
        'Amount': form.get('Amount'),
        'Creatdate': f"{now_time()}(改)",# "datetime('now','localtime')"
        'note': form.get('note')
    }
    db.revise('Accounting', data, ['id', id])
    return redirect(f'/alert/於{now_time()}修改成功')

@accounting_bp.route('/database/delete/<id>', methods=['GET'])
@login_required_role.user
def delete(id):
    if current_user.rolenum > 2:  return redirect('/error/role/2')
    db.delete('Accounting', ['id', id])
    return redirect(request.referrer)

from enum import Enum
class IE(Enum):
    expenditure = '支出'
    income = '收入'

def analysis(year, month, ie='支出'):
    data = db(f"""
        SELECT 
            Category,
            SUM(Amount) AS TotalAmount
        FROM        Accounting
        WHERE       ie = '{ie}' AND Datestamp BETWEEN {timestamp(year,month)} AND {timestamp(year,int(month)+1,dsecond=-1)}
        GROUP BY    Category

        UNION ALL

        SELECT 
            '總額' AS Category,
            SUM(Amount) AS TotalAmount
        FROM        Accounting
        WHERE       ie = '{ie}' AND Datestamp BETWEEN {timestamp(year,month)} AND {timestamp(year,int(month)+1,dsecond=-1)};
        """)
    j:dict = current.config(f'ie_class/{ie}').copy()
    for i in data:
        j[i[0]] = i[1]
    
    for key, value in j.items():
        if isinstance(value, (list, str)) or value == None:
            j[key] = 0
    return j