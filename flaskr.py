# all the imports
# coding:utf-8
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

from contextlib import closing
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqlamodel import ModelView

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_ROOT = os.path.join(BASE_DIR, 'data/flaskr.db')
# configuration
DATABASE = DATA_ROOT
DEBUG = True
SECRET_KEY = '\x0f\x8d\xcc\xaeR\xfe\x90\x94\x9907\xbe\x97\xfb\x85\x90\xe9\xc5\xb2\x0e52\xa6v'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)


app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
admin = Admin(app, name=u'项目名称')

# Add administrative views here
class MyView(BaseView):
    @expose('/')
    def index(self):
        return self.render('index.html')

admin.add_view(MyView(name='Hello 1', endpoint='test1', category='Test'))
admin.add_view(MyView(name='Hello 2', endpoint='test2', category='Test'))
admin.add_view(MyView(name='Hello 3', endpoint='test3', category='Test'))
# admin.add_view(ModelView(User, db.session))


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    g.db.close()

@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run()