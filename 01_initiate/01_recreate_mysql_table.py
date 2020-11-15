#!/usr/bin/python3


import sys
sys.path.insert(0, "/usr/local/lib/python3.8/site-packages")

import pymysql

user = "miles"
password = "milespwd"
database_name = "miles"

# Open mysql database connection

mysql_conn = pymysql.connect("localhost", user, password, database_name)

# prepare a cursor object using cursor() method
mysql_cursor = mysql_conn.cursor()


def create_tickets_table(mysql_cursor):

   # Drop table if it already exist using execute() method.
   mysql_cursor.execute("DROP TABLE IF EXISTS ticket")

   # Create table as per requirement
   ticket_sql = """CREATE TABLE ticket (
      ID int NOT NULL AUTO_INCREMENT,
      USER_ID  CHAR(100) NOT NULL,
      FLIGHT_COMPANY CHAR(100) NOT NULL,
      FLIGHT_GROUP CHAR(50) NOT NULL,
      FLIGHT_DATE DATETIME NOT NULL,
      ARRIVAL_DATE DATETIME NOT NULL,
      ORIGIN_AIRPORT  CHAR(50) NOT NULL,
      DEST_AIRPORT  CHAR(50) NOT NULL,
      TARIFF  CHAR(50) NOT NULL,
      STATUS INT NOT NULL,
      DISTANCE INT NOT NULL,
      ZONE CHAR(100) NOT NULL,
      PRIMARY KEY (ID))"""

   print("Executing: "+ticket_sql)

   # Create table
   mysql_cursor.execute(ticket_sql)

   # Check if table was created by running a query.
   mysql_cursor.execute("select * from ticket")
   
   results = mysql_cursor.fetchall()

   print("(Table creation) "+str(len(results))+" tickets found.")


# --------> Program Starts here

# Command tickets table creation.
create_tickets_table(mysql_cursor)


# disconnect from database
mysql_conn.close()
