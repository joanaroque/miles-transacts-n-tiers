#!/usr/bin/python3

import sys
sys.path.insert(0, "/usr/local/lib/python3.8/site-packages")

import pymssql
import csv



import pymysql
import random
import datetime

user = "miles"
password = "milespwd"
database_name = "miles"


def clean_and_insert_distances():
    flight_distance_dict = {}
  
    with open("flights-records.csv", newline="") as csvfile:
        flights = csv.reader(csvfile,delimiter=',',quotechar='"')
        
        # Moves the CSV to the second row, bypassing the header.
        next(flights)

        for flight in flights:
            print("origin_airport: "+flight[7] +
                  "|dest_airport:"+flight[8]+"|distance: "+flight[17])

            origin_airport = flight[7]
            dest_airport = flight[8]
            distance = int(flight[17])

            key = origin_airport+"_"+dest_airport

            if key not in flight_distance_dict:
                flight_distance_dict[key] = (
                    origin_airport, dest_airport, distance)

    return flight_distance_dict



def getRandomFlightDate():    
    # random until 160 days back from today.
    delta_days = random.randint(1, 160)

    now = datetime.datetime.now()

    flight_date = now - datetime.timedelta(days=delta_days)
    return flight_date

def getRandomArrivalDate(flight_date, hours_diff):    
    arrival_date = flight_date + datetime.timedelta(hours=hours_diff)
    return arrival_date

def getTariff():
    tariffs = ["Desconto", "Basico", "Classica", "Plus", "Executiva", "Top"]
    return random.choice(tariffs)


def getRandomUserId(users):
    return random.choice(users)

def getZone():   
    zones = ["ENA", "INTER"]
    return random.choice(zones)

def getFlightCompany():
    flight_companies = {
        "Cinel Air Miles" : "StarAlliance",
        "TAP" : "StarAlliance",
        "Emirates" : "Skywards Group",
        "AirFrance" : "Azul"
    }
    return random.choice(list(flight_companies.items()))


def createTicket(mysql_db, mysql_cursor, flight_distance_dict, users):

    flight = random.choice(list(flight_distance_dict.values()))

    origin_airport = flight[0]
    dest_airport = flight[1]
    distance = flight[2]

    user_id = getRandomUserId(users)

    flight_company, flight_company_group = getFlightCompany()

    flight_date = getRandomFlightDate()
    
    difference_hours = random.randint(1, 12)
    arrival_date = getRandomArrivalDate(flight_date, difference_hours)

    tariff = getTariff()

    zone = getZone()


    # Prepare SQL query to INSERT a record into the database.

    sql = "INSERT INTO ticket(USER_ID, FLIGHT_COMPANY, FLIGHT_GROUP, \
    FLIGHT_DATE, ARRIVAL_DATE, ORIGIN_AIRPORT, DEST_AIRPORT,TARIFF, STATUS, DISTANCE, ZONE) \
    VALUES ('%s','%s','%s','%s', '%s', '%s', '%s', '%s' ,'%d', '%d','%s'  )" % \
        (user_id, flight_company, flight_company_group, flight_date.strftime('%Y-%m-%d %H:%M:%S'),
         arrival_date.strftime('%Y-%m-%d %H:%M:%S'), origin_airport, dest_airport, tariff, 0, distance, zone)

    print(sql)

    try:
        # Execute the SQL command
        mysql_cursor.execute(sql)
        # Commit your changes in the database
        mysql_db.commit()
    except:
        # Rollback in case there is any error
        mysql_db.rollback()


def getUsers(sqlserver_cursor):

    user_sql = """select * 
                 from AspNetUsers
                 where Tier > 0"""

    sqlserver_cursor.execute(user_sql)

    users = []
    for user_info in sqlserver_cursor:
        users.append(user_info["Id"])

    return users


# --------> Program Starts here

# Open mysql database connection

mysql_db = pymysql.connect("localhost", user, password, database_name)

# Open SQL Server database connection
sqlserver_conn = pymssql.connect(server='CinelAirMilesBackOffice.mssql.somee.com',
                                 user='airCinelMiles_SQLLogin_1', password='ruft2orp5h',
                                 database='CinelAirMilesBackOffice', autocommit=True)


mysql_cursor = mysql_db.cursor()
sqlserver_cursor = sqlserver_conn.cursor(as_dict=True)

flight_distance_dict = clean_and_insert_distances()

users = getUsers(sqlserver_cursor)

try:
    #Create n tickets
    for i in range(100):
        createTicket(mysql_db, mysql_cursor, flight_distance_dict, users)
except Exception as err:
    print('Handling run-time error:', err)
    mysql_db.close()
    sqlserver_conn.close()

mysql_db.close()
sqlserver_conn.close()
