# https://blog.csdn.net/qq_42265220/article/details/120670267
#? strftime('%Y-%m-%d', timestamp, 'unixepoch','localtime')
from flask import Flask
from utils.utils import timestamp as _timestamp
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, model
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
        nullable=False, 
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
        >>> db.Column(db.Integer, unique=True, nullable=True, autoincrement=True, primary_key=True)
        ```"""
        return self.Column(db.Integer, unique=True, nullable=True, autoincrement=True, primary_key=True)
    
    def add(self, instance:model.Model, commit:bool = True):
        # assert self.Model in instance, 'Model not found.'
        self.session.add(instance)
        if commit: self.commit()

    def commit(self) -> None:
        self.session.commit()
    
    def close(self) -> None:
        self.session.close()

db = SQLAlchemy()
# db.create_all()

class User(db.Model):
    __tablename__ = 'account'
    id = db.pk
    username = db.Column(db.Text, nullable=True, unique=True)
    password = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, nullable=False, default='user')

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
    id = db.pk
    event = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.Integer, nullable=False)
    interval = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Text, nullable=True)

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
