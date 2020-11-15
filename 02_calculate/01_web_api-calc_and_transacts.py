#!/usr/bin/python3


import sys
import gc
gc.collect()
# forces python 3 on the environment. Problems with pip.
sys.path.insert(0, "/usr/local/lib/python3.8/site-packages")

import pymysql
import pymssql

import datetime
import random

from flask import Flask

app = Flask(__name__)

# --------> Program Starts here when Web API is called on localhost:5000

@app.route('/')
def start():

    # Open database connection
    user = "miles"
    password = "milespwd"
    database_name = "miles"

    # Open connection to MySQL database
    mysql_conn = pymysql.connect("localhost", user, password, database_name)

    mysql_cursor = mysql_conn.cursor()

    tickets_select_sql = "SELECT * FROM ticket \
        WHERE status = '%d'" % (0)

    # Open connection to SQLServer database
    sqlserver_conn = pymssql.connect(server='CinelAirMilesBackOffice.mssql.somee.com',
                                 user='airCinelMiles_SQLLogin_1', password='ruft2orp5h',
                                 database='CinelAirMilesBackOffice', autocommit=True)
                                 
    sqlserver_cursor = sqlserver_conn.cursor(as_dict=True)

    num_unproc_tickets = 0
    num_proc_tickets = 0

    try:
        # Execute the SQL command
        mysql_cursor.execute(tickets_select_sql)

        results = mysql_cursor.fetchall()

        num_unproc_tickets = str(len(results))



        print("Number of tickets to be processed="+num_unproc_tickets)

        for row in results:
            ticket_id = row[0]
            user_id = row[1]
            flight_company = row[2]
            flight_company_group = row[3]
            flight_date = row[4]
            arrival_date = row[5]
            orig_airport = row[6]
            dest_airport = row[7]
            tariff = row[8]
            status = row[9]
            distance = row[10]
            zone = row[11]
            
            # Now print fetched result
            #print("tickets="+str(row));
            try:
                calculate(sqlserver_cursor, user_id, flight_company, flight_company_group,
                            flight_date, arrival_date,
                        orig_airport, dest_airport, tariff, distance, zone)
                        
                update_ticket_to_processed(mysql_conn, mysql_cursor, ticket_id)

                num_proc_tickets = num_proc_tickets + 1
            except Exception as err:
                print("[ERROR] Error inserting tx for ticket_id "+str(ticket_id) +
                      " with distance: "+str(distance)+" for user_id "+user_id, err)
    except Exception as err:
        print("[Error] Error running web api and tx insert", err)
        sqlserver_conn.close()

    sqlserver_conn.commit()
    sqlserver_conn.close()

    mysql_conn.close()

    return "Number of unprocessed tickets was: "+str(num_unproc_tickets)+" | processed: "+str(num_proc_tickets)


def update_ticket_to_processed(mysql_conn, mysql_cursor, ticket_id):
    # Prepare SQL query to INSERT a record into the database.
    sql = "update ticket \
        set status = '%d' WHERE ID = '%d' " % (1, ticket_id)
    try:
        # Execute the SQL command
        mysql_cursor.execute(sql)
        # Commit your changes in the database
        mysql_conn.commit()
    except:
        # Rollback in case there is any error
        mysql_conn.rollback()


def insert_transactions(sqlserver_conn, user_id, status_miles, bonus_miles):

    now = datetime.datetime.now()
    transaction_type_credit = 0

    if status_miles > 0:
        miles_type_status = 1

        status_sql = "INSERT INTO Transactions(Price,UserId, StartBalance, EndBalance, Value, TransactionType,MilesType, Status, CreatedById, CreateDate, UpdateDate) \
            VALUES (%d,'%s',%d,%d,%d, %d, %d, %d, '%s', '%s', '%s')" % \
            (0,user_id, 0, 0, status_miles, transaction_type_credit, miles_type_status, 0,
            user_id, now.strftime('%Y-%m-%d %H:%M:%S'), now.strftime('%Y-%m-%d %H:%M:%S'))
        
        #print("STATUS_SQL -> "+status_sql)
        sqlserver_conn.execute(status_sql)



    if bonus_miles >0:
        miles_type_bonus = 0

       #print("Inserting bonus tx")
        bonus_sql = "INSERT INTO Transactions(Price,UserId, StartBalance, EndBalance, Value, TransactionType,MilesType, Status, CreatedById, CreateDate, UpdateDate) \
            VALUES (%d,'%s',%d,%d,%d, %d, %d, %d, '%s', '%s', '%s')" % \
            (0,user_id, 0, 0, bonus_miles, transaction_type_credit, miles_type_bonus, 0,
            user_id, now.strftime('%Y-%m-%d %H:%M:%S'), now.strftime('%Y-%m-%d %H:%M:%S'))

        #print("BONUS_SQL -> "+bonus_sql)
        sqlserver_conn.execute(bonus_sql)

def get_tariff_discount(tariff, zone):
    perc_multiplier = 0
    if zone == "ENA":
        if tariff == "Desconto":
            perc_multiplier = 0.4
        elif tariff == "Basico":
            perc_multiplier = 0.4
        elif tariff == "Classica":
            perc_multiplier = 0.7
        elif tariff == "Plus":
            perc_multiplier = 1
        elif tariff == "Executiva":
            perc_multiplier = 1.5
        elif tariff == "Top":
            perc_multiplier = 2
    else:
        if tariff == "Desconto":
            perc_multiplier = 0.4
        elif tariff == "Basico":
            perc_multiplier = 0.5
        elif tariff == "Classica":
            perc_multiplier = 1
        elif tariff == "Plus":
            perc_multiplier = 1.5
        elif tariff == "Executiva":
            perc_multiplier = 1.5
        elif tariff == "Top":
            perc_multiplier = 2
    return perc_multiplier

def calculate(sqlserver_cursor, user_id, flight_company, flight_company_group,
             flight_date, arrival_date, orig_airport, dest_airport,
            tariff, distance, zone):

    if flight_company_group == "StarAlliance":

        sqlserver_cursor.execute(
            'SELECT * FROM AspNetUsers WHERE Id=%s', user_id)

        for current_user in sqlserver_cursor:
            print("Executing for user "+user_id)

            current_tier = current_user["Tier"]
            total_status_miles = current_user["StatusMiles"]
            total_bonus_miles = current_user["BonusMiles"]

            perc_multiplier = get_tariff_discount(tariff, zone)

            is_gold = current_tier == 3
            is_silver = current_tier == 2
            
            tier_status_miles = 0
            tier_bonus_miles = 0

            if is_silver:
                tier_status_miles = 0.25 * total_status_miles
                tier_bonus_miles = 0.25 * total_bonus_miles
            elif is_gold:
                tier_status_miles = 0.5 * total_status_miles
                tier_bonus_miles = 0.5 * total_bonus_miles

            status_miles = (distance * perc_multiplier) + tier_status_miles
            bonus_miles = tier_bonus_miles

            print("--> Inserting transaction for user_id: " + user_id+"| tier: "+str(current_tier)+
                  "|distance: "+str(distance)+"|perc_multiplier: "+str(perc_multiplier) +
                   " | status_miles: "+str(status_miles)+" | tier_bonus_miles: "+str(tier_bonus_miles) +
                  " | bonus_miles: "+str(bonus_miles)+"|tariff: "+tariff+"|zone: "+zone)


            #insert status miles in transactions table
            insert_transactions(sqlserver_cursor, user_id,
                               status_miles, bonus_miles)
    else:
        print(
            f"Current ticket is not from a Star Alliance company. {flight_company_group}")



