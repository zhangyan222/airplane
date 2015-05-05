#!/usr/bin/python
## encoding: utf-8
from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)
#fakedata_t = { 'source' : '北京',
#             'dest' : '上海',
#             'id' : 'KN5987',
#             'date' : '1970-1-1',
#             'start' : '07:00',
#             'end' : '09:00' }
fakedata_t = [ '北京', '上海', 'KN5987', '1970-1-1', '07:00', '09:00' ]


@app.route("/submit", methods=['POST'])
def book_post():
    fakedata = fakedata_t
    fakedata[0] = request.form['source']
    fakedata[1] = request.form['destination']
    fakedata[3] = request.form['date']
    return render_template('book_result.html',
                           source = request.form['source'],
                           destination = request.form['destination'],
                           date = request.form['date'],
                           results=[fakedata])

@app.route("/book", methods=['GET'])
def book():
    return render_template('book.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True )
