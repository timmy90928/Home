# https://blog.csdn.net/qq_42265220/article/details/120670267
# https://www.maxlist.xyz/2019/10/30/flask-sqlalchemy/
#? strftime('%Y-%m-%d', timestamp, 'unixepoch','localtime')

"""

## Migrate
### init
set FLASK_APP=server_run.py
flask db init

### 後續
- 將資料庫的`alembic_version`表刪除
- 將`migrations/versions`資料夾內的檔案刪除

"""
from flask import Flask
from utils.utils import timestamp as _timestamp, now_time
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, model
from alembic.config import Config as _AlembicConfig
from alembic import command as _AlembicCommand
from flask_migrate import Migrate
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Text, desc
from utils.utils import hash
class SQLAlchemy(_SQLAlchemy):

    __table_args__ = {'extend_existing': True}
    __tablename__ = ''
    Integer = Integer
    String = String
    Date = Date
    Float = Float
    Text = Text
    ForeignKey = ForeignKey

    def __init__(self, app:Flask  = None):
        """
        Initialize an instance of SQLAlchemy.

        ```
        db = SQLAlchemy()
        db.add()
        db.session.delete()
        ```
        """
        super().__init__(app)
    
    def __call__(self, sql:str):
        """
        >>> db = SQLAlchemy()
        >>> result = db('select * from account')
        """
        return self.session.execute(sql)
    
    def Column(
        self, 
        _type, 
        *,
        nullable=True, 
        primary_key=False, 
        autoincrement=False, 
        unique=False, 
        default=None, 
        name=None, 
        foreignKey=None, 
        **kwargs
    ):
        return Column(_type, 
                      foreignKey, 
                      nullable=nullable, 
                      primary_key=primary_key, 
                      autoincrement=autoincrement, 
                      unique=unique, 
                      default=default,
                      name=name, 
                      **kwargs 
        )
    
    @property
    def pk(self):
        """```
        >>> db.Column(db.Integer, unique=True, nullable=False, autoincrement=True, primary_key=True)
        ```"""
        return self.Column(db.Integer, unique=True, nullable=False, autoincrement=True, primary_key=True)
    
    def add(self, instance:model.Model, commit:bool = True):
        # assert self.Model in instance, 'Model not found.'
        self.session.add(instance)
        if commit: self.commit()

    def commit(self) -> None:
        self.session.commit()
    
    def close(self) -> None:
        self.session.close()


db = SQLAlchemy()

def initDB(app:Flask, create_all:bool = True):
    global db
    db.init_app(app)
    migrate = Migrate()
    migrate.init_app(app, db)
    alembic_cfg = _AlembicConfig("migrations/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", app.config['SQLALCHEMY_DATABASE_URI'])
    alembic_cfg.set_main_option("script_location", "migrations")
    
    
    ###* APP Context ###
    with app.app_context():
        if create_all:
            db.create_all()
            _AlembicCommand.revision(alembic_cfg, message=f"Update from {now_time()}", autogenerate=True) # 設定遷移訊息
            _AlembicCommand.upgrade(alembic_cfg, "head") # 執行升級（將變更應用到資料庫）
            

class User(db.Model):
    __tablename__ = 'account'
    id = db.pk
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text)
    name = db.Column(db.Text)
    role = db.Column(db.Text,nullable=False,  default='user')

    def __init__(self, username, password, name, role):
        self.username = username
        self.password = hash(password)
        self.name = name
        self.role = role

    def check_password(self, password):
        """
        ```
        user = User.query.filter_by(username="john_doe").first()
        if user.check_password("securepassword"):
            print("Password is correct")
        ```
        """
        return hash(password) == self.password

    def __repr__(self):
        return '<User %r>' % self.username
    
class Record(db.Model):
    __tablename__ = 'Record'
    id = db.pk
    event = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.Integer)
    interval = db.Column(db.Integer)
    note = db.Column(db.Text)

    def __init__(self, event, time:str, note):
        _now_timestamp = int(_timestamp(string=time))
        interval = None if len(Record.query.filter_by(event=event).all()) == 0 else _now_timestamp - int(Record.query.filter_by(event=event).order_by(Record.timestamp.desc()).first().timestamp)

        self.event = event
        self.timestamp = _now_timestamp
        self.interval = int(interval/86400) if interval else None #! Day
        self.note = note
    def convertInterval(self):
        return self.interval / 86400
    def __repr__(self):
        return '<Record %r>' % self.event
class Accounting(db.Model):
    __tablename__ = 'Accounting'
    id = db.pk
    Datestamp = db.Column(db.Text)
    ie = db.Column(db.Text, nullable=False)
    Amount = db.Column(db.Text, nullable=False)
    Category = db.Column(db.Text, nullable=False)
    Detail = db.Column(db.Text)
    note = db.Column(db.Text, default='')
    link = db.Column(db.Text, default='')
    Creatdate = db.Column(db.Text, default=now_time())

class Travel(db.Model):
    __tablename__ = 'travel'
    id = db.pk
    name = db.Column(db.Text)
    datestamp = db.Column(db.Text)
    place = db.Column(db.Text)
    people = db.Column(db.Text)
    note = db.Column(db.Text, default='')
    position = db.Column(db.Text)
    # link = db.Column(db.Text)

