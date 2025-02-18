from . import *
from utils.g import current_user, current

db = current.db
travel_bp = Blueprint('travel', __name__, url_prefix='/travel')

HEADS = ['流水號','行程名稱','日期','類別','地點','人員','備註','編輯','刪除']  
HEADS_SQL = "id,name,strftime('%Y-%m-%d', datestamp, 'unixepoch','localtime'),category,place,people,note"

@travel_bp.route('/', methods=['GET'])
@login_required
def index():
    datas = db.get_col('travel',HEADS_SQL,customize=' ORDER BY datestamp DESC')
    datas = [add_small_button(*_, blue=['編輯',f'/travel/edit/{_[0]}'], red=[f'是否要刪除 {_[1]} (ID={_[0]})',f'/travel/delete/{_[0]}' ]) for _ in datas]
    return render_template('travel/travel.html',title='行程紀錄',datas=datas,heads=HEADS)

@travel_bp.route('/add', methods=['GET'])
@login_required_role.user
def add():
    if current_user.rolenum > 2:  return redirect('/error/role/2')
    return render_template('travel/add.html',options=options_default())

@travel_bp.route('/edit/<id>', methods=['GET'])
@login_required_role.user
def editdata(id):
    if current_user.rolenum > 2:  return redirect('/error/role/2')
    datas = db.get_row('travel', ['id', id],HEADS_SQL)[0]
    position = db.get_row('travel', ['id', id],'position')[0]
    return render_template('travel/add.html',datas=datas,options=options_default(),position=position[0])

@travel_bp.route('search', methods=['GET','POST'])
@login_required
def search():
    if request.method == 'POST':
        form = request.form
        data = {
            'name': form.get('name') if form.get('name') else '%',
            'category': form.get('class') if form.get('class') else '%',
            'place': form.get('place') if form.get('place') else '%',
            'people': form.get('people') if form.get('people') else '%',
            'note': form.get('note') if form.get('note') else '%',
        }
        date = f"AND datestamp BETWEEN {timestamp(string=form.get('startDate'))} AND {timestamp(string=form.get('endDate'))}" if form.get('startDate') and form.get('endDate') else ''
        datas = db.get_col('travel', HEADS_SQL, data, customize=f'{date} ORDER BY datestamp DESC')
        datas = [add_small_button(*_, blue=['編輯',f'/travel/edit/data/{_[0]}'], red=[gettext("Do you want to delete %(name)s (ID=%(id)s)?", id=_[0], name=_[1]),f'/travel/database/delete/{_[0]}' ]) for _ in datas]
        return render_template('travel/search.html',options=options_default(), datas=datas, heads=HEADS)

    return render_template('travel/search.html',options=options_default())

@travel_bp.route('/map', methods=['GET'])
@login_required
def travel_map():
    pp = ''
    for n, (place,date,pos) in enumerate(db.get_col('travel', "place,strftime('%Y-%m-%d', datestamp, 'unixepoch','localtime'),position")):
        if not pos or pos=='None' or pos=='': continue
        if n == 0:
            pp += f"{place},{date},{pos}"
        else:
            pp += f";{place},{date},{pos}"
    return render_template('travel/travel_map.html',position=pp)
@travel_bp.route('database/add', methods=['POST'])
@login_required_role.user
def data_add():
    form = request.form
    data = {
        'name': form.get('name'),
        'datestamp': timestamp(string=form.get('date')),
        'category': form.get('class'),
        'place': form.get('place'),
        'people': form.get('people'),
        'note': form.get('note'),
        'position': form.get('gps'),
    }
    # print(db.get_row('travel', ['name',data['name']]))
    db.add('travel', data)
    return redirect(f'/alert/於{now_time()}新增成功?to=/travel')

@travel_bp.route('/database/revise/<id>', methods=['POST'])
@login_required_role.user
def data_revise(id):
    form = request.form
    data = {
        'name': form.get('name'),
        'datestamp': timestamp(string=form.get('date')),
        'category': form.get('class'),
        'place': form.get('place'),
        'people': form.get('people'),
        'note': form.get('note'),
        'position': form.get('gps'),
    }
    db.revise('travel', data, ['id', id])
    return redirect(f'/alert/於{now_time()}修改成功?to=/travel')
@travel_bp.route('database/delete/<id>', methods=['GET'])
@login_required_role.user
def data_delete(id):
    if current_user.rolenum > 2:  return redirect('/error/role/2')
    db.delete('travel', ['id', id])
    return redirect(request.referrer)

def options_default():
    options = {}
    options['name'] = db.get_col('travel', 'name',distinct=True ,customize = ' ORDER BY datestamp DESC')
    options['place'] = db.get_col('travel', 'place',distinct=True ,customize = ' ORDER BY datestamp DESC')
    options['category'] = [('百岳',),('小百岳',),('郊山或健行',),('休閒',),('海外',)]
    options['people'] = db.get_col('travel', 'people',distinct=True ,customize = ' ORDER BY datestamp DESC')
    return options