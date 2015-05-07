#!/usr/bin/python
## encoding: utf-8
import sqlite3
from flask import Flask
from flask import render_template
from flask import request, redirect, g

app = Flask(__name__)
DATABASE = 'db/database.db'

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
    results = query_db('select \
                       printf("%s(%s)", d.airport_name, d.city) as depart, \
                       printf("%s(%s)", a.airport_name, a.city) as arrive, \
                       company_name, flight.flight_id as flight_id, \
                       dtime, atime, \
                       prize.prize as prize \
                       from flight left join airport_city d on depart_id = d.airport_id \
                       left join airport_city a on arrive_id = a.airport_id \
                       left join company_name c on flight.company_id = c.company_id \
                       left join prize \
                       on flight.flight_id = prize.flight_id \
                       where d.city = ? and a.city = ? and ? between prize.begin_time and prize.end_time; \
             ', (request.form['source'], request.form['destination'], request.form['date']))
    return render_template('book_result.html',
                           source = request.form['source'],
                           destination = request.form['destination'],
                           date = request.form['date'],
                           results=results)

@app.route("/buy", methods=['POST'])
def buy():
    prize = query_db('select prize from prize \
                     where flight_id = ? and \
                     ? between begin_time and end_time \
                     order by operate_time desc;',
                     (request.form['ano'], request.form['date']),
                     one=True)['prize'];
    return render_template('buy.html',
                           ano = request.form['ano'],
                           date = request.form['date'],
                           prize = prize)

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
    if request.form['pay_type'] == 'fake': # FIXME
        cur = get_db().cursor()
        cur.execute('insert into purchase \
                    values(NULL, ?, ?, "fake", ?, 0);',
                    (request.form['ano'], request.form['date'],
                     prize))
        tid = query_db('select last_insert_rowid() \
                       from purchase;', one=True)['last_insert_rowid()']
        get_db().commit() # ?
        return redirect("/fake_pay_success?tid={}".format(tid))

@app.route("/fake_pay_success", methods=['GET']) # FIXME
def fake_pay_success():
    cur = get_db().cursor()
    tid = unicode(request.args['tid'])
    print type(tid)
    print tid
    cur.execute('update purchase set purchased = 1 where tid = {}'.format(tid)); # ???
    results = query_db('select * from purchase where tid = {}'.format(tid), one=True)
    print results
    get_db().commit()
    return render_template('fake_pay_success.html', results=results)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True )
