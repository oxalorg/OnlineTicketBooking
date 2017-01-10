from flask import Flask
from flask import request
from flask import render_template
import sqlite3
from contextlib import closing
from flask import g
from flask import session, redirect, url_for, \
             abort, flash
from random import randint

app = Flask(__name__)

# CONFIGURATIONS
DATABASE = '/tmp/book.db'
USERNAME = 'admin'
PASSWORD = 'admin'
SECRET_KEY = 'jsdnfjasdnhaf'
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect('/tmp/book.db')

@app.before_request
def before_request():
        g.db = connect_db()


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


#@app.route('/')
def index():
    print("Index")
    return render_template('index.html')


#def valid_login(userid, password):
#    cur = g.db.execute('''SELECT userid, password from users''')
#    entries = [dict(users=row[0], passwords=row[1]) for row in cur.fetchall()]
#    print(entries) 
#    if (userid, password) in (entries.getkeys(), entries.getvalues()):
#        return True
#    else:
#        return False

@app.route('/')
def show_entries():
    price = 0
    cur = g.db.execute('select train, seat, empty from entries')
    entries = [dict(train=row[0], seat=row[1], price=randint(400,2300)) for row in cur.fetchall() if row[2] == 0]
    return render_template('show_entries.html', entries=entries, price=price)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['userid'] != app.config['USERNAME']:
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


@app.route('/addticket', methods=['GET', 'POST'])
def addticket():
    error = None
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'POST':
        g.db.execute('insert into entries (train, seat, empty) values (?, ?, 0)',
                [request.form['train'], request.form['seat']])
        g.db.commit()
        flash('New entry was successfull posted')
    return render_template('addticket.html', error=error)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('UPDATE entries SET empty=1 WHERE seat=(?)',
                 [request.form['pseat']])
    g.db.commit()
    flash('Ticket is on-hold, proceed to payment to CONFIRM the ticket.')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.debug = True
    app.run()
