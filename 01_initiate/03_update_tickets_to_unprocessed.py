#!/usr/bin/python3
import sys

sys.path.insert(0, "/usr/local/lib/python3.8/site-packages")

import datetime
import random
import pymysql
import csv

# --------> Program Starts here.
# This script is only to be called in case we dont want to delete all tickets.

user = "miles"
password = "milespwd"
database_name = "miles"

mysql_db = pymysql.connect("localhost", user, password, database_name)

mysql_cursor = mysql_db.cursor()

mysql_cursor.execute("update ticket set status = 0")
mysql_db.commit()

mysql_cursor.execute("select * from ticket where status = 0")
# Fetch all the rows in a list of lists.
results = mysql_cursor.fetchall()

print("We have "+str(len(results))+" unprocessed tickets")

mysql_db.close()
