from .model import User, Record, Accounting, Travel, Setting, db
from utils.g import current

from flask import Flask
from flask_admin import Admin, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin

class IndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin.html')

def initAdmin(app:Flask):
    ###* Index View ###
    admin = Admin(app, name=app.config['TITLE'], template_mode='bootstrap3', index_view=IndexView())

    ###* File View ###
    admin.add_view(FileAdmin('c:\\', name='File Manager', endpoint='/file_manager'))
    admin.add_view(FileAdmin(current.config.get('blog/path'), name='Blog Images', endpoint='/blog'))

    ###* Model View ###
    admin.add_view(ModelView(User, db.session, 'User Manager', endpoint='/account', category="DataBase"))
    admin.add_view(ModelView(Accounting, db.session, 'Accounting', endpoint='/accounting', category="DataBase"))
    admin.add_view(ModelView(Record, db.session, 'Record', endpoint='/record', category="DataBase"))
    admin.add_view(ModelView(Travel, db.session, 'Travel', endpoint='/travel', category="DataBase"))
    admin.add_view(ModelView(Setting, db.session, name='Setting', endpoint='/setting', category="DataBase"))
    return admin
