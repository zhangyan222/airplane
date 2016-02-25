#!/usr/bin/python
## encoding: utf-8
import re
import urllib
import thread
import sqlite3
import datetime
import ConfigParser
from flask import g
from flask import Flask
from flask import render_template
from flask import send_from_directory
from flask import request, redirect, abort

from send_mail import simply_sendmail

app = Flask(__name__)
DATABASE = 'db/database.db'
CONFIGFILE = 'db/main.cfg'

config = ConfigParser.ConfigParser()
config.readfp(open(CONFIGFILE))

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = make_dicts
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/submit", methods=['POST'])
def book_post():
    try:
        assert(request.form['source'] != '')
        assert(request.form['destination'] != '')
        date = datetime.datetime.strptime(request.form['date'], '%Y-%m-%d')
    except (AssertionError, ValueError, KeyError):
        abort(400)

    results = query_db('select * from plane_table where dcity = ? and acity = ? \
                       and ? between begin_time and end_time;',
                       (request.form['source'], request.form['destination'],
                        request.form['date']))
    return render_template('book_result.html',
                           source = request.form['source'],
                           destination = request.form['destination'],
                           date = request.form['date'],
                           results=results)

@app.route("/buy", methods=['POST'])
def buy():
    result = query_db('select * from plane_table where flight_id = ?',
                       (request.form['ano'], ), one=True);
    return render_template('buy.html',
                           result=result, date=request.form['date'])

@app.route("/book", methods=['GET'])
def book():
    return render_template('book.html')

@app.route("/pay", methods=['POST'])
def pay():
    prize = query_db('select prize from prize \
                     where flight_id = ? and \
                     ? between begin_time and end_time \
                     order by operate_time desc;',
                     (request.form['ano'], request.form['date']),
                     one=True)['prize'];
    cur = get_db().cursor()
    cur.execute('insert into passenger \
                values(NULL, ?, ?, ?, ?, ?, ?);',
                (request.form['name'], request.form['gender'],
                 request.form['work'], request.form['card'],
                 request.form['mail'], request.form['phone']))
    passenger_id = query_db('select last_insert_rowid() \
                   from passenger;', one=True)['last_insert_rowid()']
    cur.execute('insert into purchase \
                values(NULL, ?, ?, ?, "fake", ?, 0);',
                (passenger_id, request.form['ano'], request.form['date'],
                 prize))
    tid = query_db('select last_insert_rowid() \
                   from purchase;', one=True)['last_insert_rowid()']
    get_db().commit() # ?
    if request.form['pay_type'] == 'fake': # FIXME
        return render_template("alipay.html",
                               prize=prize,
                               title=u'机票-{}-{}'.format(
                                   request.form['ano'],
                                   request.form['date']),
                               tid=tid,
                               )
    elif request.form['pay_type'] == 'fake_email': # FIXME
        thread.start_new_thread(simply_sendmail, (
            config.get("mail", "smtp_server"),
            config.get("mail", "smtp_port"),
            config.get("mail", "smtp_username"),
            config.get("mail", "smtp_password"),
            request.form['mail'],
            config.get("mail", "subject").decode("utf-8"),
            config.get("mail", "content").format(
                config.get("main", "domain"),
                urllib.urlencode({'tid':tid,
                                  'prize':prize,
                                  'date':request.form['date'],
                                  'ano':request.form['ano']}
                )
                                )))
        return render_template('mail_sent.html',
                               email=request.form['mail'])


@app.route("/mail_pay", methods=['GET'])
def mail_pay():
    tid = unicode(request.args['tid'])
    prize = unicode(request.args['prize'])
    ano = unicode(request.args['ano'])
    date = unicode(request.args['date'])
    return render_template("alipay.html",
                            prize=prize,
                            title=u'机票-{}-{}'.format(ano, date),
                            tid=tid,
                            )

@app.route("/fake_pay_success", methods=['GET']) # FIXME
def fake_pay_success():
    cur = get_db().cursor()
    tid = unicode(request.args['tid'])
    cur.execute('update purchase set purchased = 1 where tid = ?', (tid, )); # ???
    results = query_db('select * from e_ticket \
                       where tid = ?', (tid, ), one=True)
    get_db().commit()
    return render_template('fake_pay_success.html', results=results)

@app.route('/css/<path:path>')
def css(path):
    return send_from_directory('css', path)

@app.route('/js/<path:path>')
def js(path):
    return send_from_directory('js', path)

@app.route('/alipay_files/<path:path>')
def alipay_files(path):
    return send_from_directory('alipay_files', path)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True )
