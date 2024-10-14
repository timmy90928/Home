from . import Blueprint, render_template, request, redirect, login_required, current_user, db, jsonify, CONFIG, now_time, timestamp
from utils.db import IE_TOTAL_SQL

accounting_bp = Blueprint('accounting', __name__, url_prefix='/accounting')
HEADS = ['流水號','日期','收支','類別','細項','金額','備註']
HEADS_SQL = "id,strftime('%Y-%m-%d', Datestamp, 'unixepoch','localtime'),ie,Category,Detail,Amount,note"

@accounting_bp.route('/database', methods=['GET'])
# @login_required
def show_database():
    return redirect('/show/Accounting')

@accounting_bp.route('/add', methods=['GET'])
@login_required
def add():
    if current_user.rolenum > 2:  return redirect('/error/role/2')
    return render_template('accounting/add.html')

@accounting_bp.route('/<year>/<month>', methods=['GET'])
def monthly_analysis(year, month):
    # https://github.com/timmy90928/Home/issues/2
    e  = analysis(year, month, '支出')
    i  = analysis(year, month, '收入')
    e_values = list(e.values())
    i_values = list(i.values())
    datas = db(f"SELECT {HEADS_SQL} FROM Accounting WHERE Datestamp BETWEEN {timestamp(year,month)} AND {timestamp(year,int(month)+1,dsecond=-1)}")
    
    return render_template('accounting/search.html',title='月分析',month = f'{year}-{month}',t_datas = [i_values[-1],e_values[-1],int(i_values[-1])-int(e_values[-1])],
                           datas = datas, heads = HEADS,
                           e_datas = e_values, e_heads = list(e.keys()),
                           i_datas = i_values, i_heads = list(i.keys()))

@accounting_bp.route('/analysis/month', methods=['GET','POST'])
def month_analysis():
    if request.method == 'POST':
        date = request.form.get('Date')
        date = date.split('-')
    else:
        date = now_time().split(' ')[0].split('-')
    return redirect(f'/accounting/{date[0]}/{date[1]}')

@accounting_bp.route('/search', methods=['GET','POST'])
def search():
    if request.method == 'POST':
        form = request.form
        startDate = form.get('startDate') if form.get('startDate') else '%'
        endDate =   form.get('endDate') if form.get('startDate') else '%' # datetime.strptime(form.get('endDate'), "%Y-%m-%d").timestamp()
        minAmount= form.get('minAmount') if form.get('minAmount') else int(0)
        maxAmount = form.get('maxAmount') if form.get('maxAmount') else '+Infinity'
        data = {
            'ie': form.get('ie') if form.get('ie') else '%',
            'Category': form.get('Category') if form.get('Category') else '%',
            'Detail': form.get('Detail') if form.get('Detail') else '%',
            'note': form.get('note') if form.get('note') else '%'
        }
        
        date = f"AND Datestamp BETWEEN strftime('%s', '{startDate}') AND strftime('%s', '{endDate}')" if form.get('startDate') and form.get('endDate') else ''
        datas = db.get_col('Accounting', HEADS_SQL, data, 
                           customize= f" {date} AND Amount BETWEEN '{minAmount}' AND '{maxAmount}' ORDER BY Datestamp DESC")
        
        data['ie'] = '收入'
        sum_i = db.get_col('Accounting','sum(Amount)', data, 
                           customize= f" {date} AND Amount BETWEEN '{minAmount}' AND '{maxAmount}' ORDER BY Datestamp DESC")[0][0]
        sum_i = sum_i if sum_i else 0
        data['ie'] = '支出'
        sum_e = db.get_col('Accounting','sum(Amount)', data, 
                           customize= f" {date} AND Amount BETWEEN '{minAmount}' AND '{maxAmount}' ORDER BY Datestamp DESC")[0][0]
        sum_e = sum_e if sum_e else 0
        
        sum_total = int(sum_i) - int(sum_e)

        return render_template('accounting/search.html',title='搜尋', datas=datas, heads=HEADS, t_datas = [sum_i,sum_e,sum_total])

    return render_template('accounting/search.html',title='搜尋')

@accounting_bp.route('/edit/class', methods=['GET'])
def editclass():
    if current_user.rolenum > 2:  return redirect('/error/role/2')
    ie_i = CONFIG('ie_class/收入')
    ie_e = CONFIG('ie_class/支出')
    # list(CONFIG('ie_class/收入').keys())

    return render_template('accounting/editclass.html',ie_i=ie_i,ie_e=ie_e)

@accounting_bp.route('/edit/data/<id>', methods=['GET'])
def editdata(id):
    if current_user.rolenum > 2:  return redirect('/error/role/2')
    datas = db.get_row('Accounting', ['id', id],HEADS_SQL)[0] # note
    return render_template('accounting/add.html',datas=datas)

@accounting_bp.route('/getCategories', methods=['POST'])
def getCategories():
    data = request.json  # Get the JSON data in the request.
    ie = data['ie']
    Category = CONFIG(f'ie_class/{ie}')
    response = {'message': 'Received!', 'categories': Category}
    return jsonify(response)

@accounting_bp.route('/database/add', methods=['POST'])
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
    return redirect(f'/alert/於{now_time()}新增成功')

@accounting_bp.route('/database/revise/<id>', methods=['POST'])
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
    j:dict = CONFIG(f'ie_class/{ie}').copy()
    for i in data:
        j[i[0]] = i[1]
    
    for key, value in j.items():
        if isinstance(value, (list, str)) or value == None:
            j[key] = 0
    return j