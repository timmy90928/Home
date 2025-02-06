from . import *
from utils.g import current_user, current

record_bp = Blueprint('record', __name__, url_prefix='/record')

HEADS_I = ['事件','上次更改的時間',"與上次間隔(天)","平均間隔(天)","備註", "詳細紀錄"]
HEADS_I_SQL = "event,timestamp,days_since_latest,avg_interval,note"
INDEX_SQL = f"""
WITH Ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY event ORDER BY timestamp DESC) AS rn
    FROM Record
),
AverageIntervals AS (
    SELECT event,
           AVG(interval) AS avg_interval
    FROM Record
    GROUP BY event
)
SELECT r.event,
       strftime('%Y-%m-%d', r.timestamp, 'unixepoch', 'localtime') AS timestamp,
       ai.avg_interval, 
       r.note,
       CASE 
           WHEN r.timestamp IS NOT NULL THEN
               CAST(julianday('now') - julianday(strftime('%Y-%m-%d %H:%M:%S', r.timestamp, 'unixepoch', 'localtime')) AS INTEGER)
           ELSE
               NULL 
       END AS days_since_latest  
FROM Ranked r
JOIN AverageIntervals ai ON r.event = ai.event 
WHERE r.rn = 1;
"""

HEADS = ['流水號','時間', "與上次之間格(天)","備註","編輯","刪除"]
HEADS_SQL = "id,event,strftime('%Y-%m-%d', timestamp, 'unixepoch','localtime'),interval,note"

@record_bp.route('/')
def index_record():
    datas = current.db(INDEX_SQL)
    datas = [add_small_button(e, day, days_since_latest, avg_interval, note, blue=['紀錄',f'/record/{e}']) for e, day, avg_interval, note, days_since_latest in datas]
    return render_template('record/record.html', heads=HEADS_I, datas=datas)

@record_bp.route('/<event>')
def record_event(event):
    datas = current.db.get_col('Record',HEADS_SQL, {'event': event}, customize=' ORDER BY timestamp DESC')
    datas = [add_small_button(id,t, i, n, blue=['編輯',f'/record/edit/{id}'], red=[f'是否要刪除 {e} (ID={id})',f'/record/delete/{id}']) for id,e, t, i, n in datas]

    return render_template('record/record.html', heads=HEADS, datas=datas, event=event)


@record_bp.route('/add', methods=['GET'])
@login_required
def record_add():
    if current_user.rolenum > 2:  return redirect('/error/role/2')
    datas = current.db.get_col('Record','event', distinct=True)
    return render_template('record/add.html', datas=datas)
@record_bp.route('/database/add', methods=['POST'])
def record_data_add():
    if current_user.rolenum > 2:  return redirect('/error/role/2')
    form = request.form
    record = model.Record(
        time = form.get('date'),
        event = form.get('event'),
        
        note = form.get('note'),
    )
    model.db.add(record)
    return redirect(f'/alert/於{now_time()}新增成功?to=/record/add')