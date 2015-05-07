#!/bin/sh
rm database.db
sqlite3 database.db < schema.sql
sqlite3 database.db << EOS
.separator ","
.import flight.csv flight
.import airport_city.csv airport_city
.import company_name.csv company_name
.separator "|"
.import prize.csv prize
EOS
