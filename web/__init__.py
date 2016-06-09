#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""base module for web guis"""
# todo oy vey, this file is a shit show atm

from flask import Flask, g
from flask_bootstrap import Bootstrap, StaticCDN, WebCDN
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask_mail import Mail
from flask_wtf.csrf import CsrfProtect
from celery import Celery

from db import DB
from config.db import Config
from config.env import Environment

from web.routes.index import index
from web.routes.tagger import tagger
from web.routes.meta import meta

web_config = Config('web')
env = Environment()

app = Flask(__name__)
app.register_blueprint(index, url_prefix='/')
app.register_blueprint(tagger, url_prefix='/tagger')
app.register_blueprint(meta, url_prefix='/meta')


def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


worker_config = Config('worker')
app.config['CELERY_BACKEND'] = worker_config['backend']
app.config['CELERY_BROKER_URL'] = worker_config['broker']
app.config['CELERY_ALWAYS_EAGER'] = False  # important so it doesn't get executed locally!
app.config['CELERY_TASK_SERIALIZER'] = 'msgpack'
app.config['CELERY_RESULT_SERIALIZER'] = 'msgpack'
app.config['CELERY_ACCEPT_CONTENT'] = ['msgpack']
celery = make_celery(app)

Bootstrap(app)
app.extensions['bootstrap']['cdns']['bootstrap'] = StaticCDN()
app.extensions['bootstrap']['cdns']['jquery'] = WebCDN('/static/js/')

# todo turn off "allow less secure apps!"
app.config['MAIL_SERVER'] = web_config['web']['server']
app.config['MAIL_PORT'] = web_config['web']['port']
app.config['MAIL_USERNAME'] = web_config['web']['username']
app.config['MAIL_PASSWORD'] = web_config['web']['password']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

app.config['SECRET_KEY'] = web_config['secret_key']
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(username)s:%(password)s@%(host)s:%(port)s/%(database)s' % \
                                        env['DB']
app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
app.config['SECURITY_PASSWORD_SALT'] = web_config['salt']  # unnecessary but required
app.config['SECURITY_URL_PREFIX'] = '/user'
app.config['SECURITY_CONFIRMABLE'] = True
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True
app.config['SECURITY_CHANGEABLE'] = True

CsrfProtect(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define models
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Create a user to test with
@app.before_first_request
def before_first_request():
    db.create_all()


@app.before_request
def before_request():
    # todo mixing different stuff here, refactor to something more consistent
    g.celery = celery
    g.db_session = DB().session


@app.teardown_request
def teardown_request(exception):
    db_session = getattr(g, 'db_session', None)
    if db_session is not None:
        db_session.close()
    if exception is not None:
        print(exception)
