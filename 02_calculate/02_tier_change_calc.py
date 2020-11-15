#!/usr/bin/python3
import datetime
import pymssql
import sys
sys.path.insert(0, "/usr/local/lib/python3.8/site-packages")


sqlserver_conn = pymssql.connect(server='CinelAirMilesBackOffice.mssql.somee.com',
                                 user='airCinelMiles_SQLLogin_1', password='ruft2orp5h',
                                 database='CinelAirMilesBackOffice', autocommit=True)

sqlserver_cursor = sqlserver_conn.cursor(as_dict=True)

def update_tier_change(sqlserver_cursor, user_id, old_tier, new_tier,
                      num_flights, num_miles):
    print("Tier being updated from: "+str(old_tier)+" to "+str(new_tier)+" for user_id: "+str(user_id))
  
    now = datetime.datetime.now()
    now = now.strftime('%Y-%m-%d %H:%M:%S')

    sql = "INSERT INTO TierChanges(OldTier, NewTier, NumberOfFlights, NumberOfMiles, ClientId, Status, CreateDate, UpdateDate) \
         VALUES (%d,%d,%d,%d, '%s', %d, '%s', '%s' )" % \
        (old_tier, new_tier, num_flights, num_miles, user_id, 0, now, now)
    
    sqlserver_cursor.execute(sql)


def update_user_info(sqlserver_cursor, user_id, new_tier, current_tier, total_status_miles, total_bonus_miles):
    print("Updating UserID: "+str(user_id)+" with new_tier: " +
          str(new_tier)+" | StatusMiles: "+str(total_status_miles)+" | BonusMiles: "+str(total_status_miles))

    update_sql = """ update AspNetUsers
                         set Tier = %d , StatusMiles = %d, BonusMiles = %d 
                         where Id = %s """

    sqlserver_cursor.execute(update_sql, (new_tier, total_status_miles, total_bonus_miles, user_id))


def define_new_tier(user_id, current_tier, is_gold,
                    is_silver, total_status_miles,
                number_of_flights):

    new_tier = current_tier

    if (not is_gold) and (total_status_miles >= 70000 or number_of_flights >= 50):
        new_tier = 3
        print("UserID: "+str(user_id)+" changes to 'gold'.")

    elif is_gold and (total_status_miles >= 50000 or number_of_flights >= 40):
        print("UserID: "+str(user_id)+" remains the same as 'gold'.")

    elif (not is_silver) and (total_status_miles >= 30000 or number_of_flights >= 25):
        new_tier = 2
        print("UserID: "+str(user_id)+" changes to 'silver'.")

    elif is_silver and (total_status_miles >= 20000 or number_of_flights >= 15):
        print("UserID: "+str(user_id)+" remains the same as 'silver'.")
    else:
        new_tier = 1

    return new_tier


def calculate_user_new_tier(user_id, current_tier):
    
    print("Processing tier change for user_id "+user_id+" from tier: "+str(current_tier))

    # Select all transactions since one year ago for current user for miles type 'status'.
    tx_sql = """select * 
                from Transactions
                where UserId = %s                     
                and CreateDate > DATEADD(year,-1,GETDATE()) """
    

    
    sqlserver_cursor.execute(tx_sql, user_id)

    # Initialize variables
    number_of_flights = 0
    total_status_miles = 0
    total_bonus_miles = 0

    is_gold = current_tier == 3
    is_silver = current_tier == 2

    # Reads all transactions for the current user in a space of a year.


    for transaction in sqlserver_cursor:
        miles_type = transaction["MilesType"]
        
        #If current tx is for status miles
        if miles_type == 1:
            number_of_flights = number_of_flights + 1

            total_status_miles = total_status_miles + transaction["Value"]
        #If current tx is for bonus miles
        else:
            total_bonus_miles = total_bonus_miles + transaction["Value"]

    # If current user did not flew this past year
    if number_of_flights == 0:
        print("This past year, UserID "+str(user_id)+" has not travelled.")
    else:
        print("This past year, UserID "+str(user_id)+" has travelled "+str(number_of_flights)+" time(s).")
        
        # Check if new tier should be set, or --> keep the same <---
        new_tier = define_new_tier(user_id,current_tier,
                                    is_gold, is_silver, total_status_miles,
                                        number_of_flights)
        
        # Updating user information with status, bonus miles and tier.    
        update_user_info(sqlserver_cursor, user_id,
                            new_tier, current_tier, 
                            total_status_miles, total_bonus_miles)
        
        # Evaluate if tier change should be done.
        if current_tier != new_tier:
            update_tier_change(sqlserver_cursor, user_id,
                                current_tier, new_tier,
                                number_of_flights, total_status_miles)
        else:
            print("Current userID: "+user_id+" is remaining in tier: "+str(current_tier))
    
 
# Entry method
def calculate_users_tier_change():

    # for each user on 'users' table, calculate tier changes
    user_sql = """select * 
                 from AspNetUsers
                 Where Tier > 0"""

    sqlserver_cursor.execute(user_sql)


    rows = sqlserver_cursor.fetchall()
    print("Processing tier change for " +
          str(sqlserver_cursor.rowcount)+" users.")

    for user_info in rows:
        user_id = user_info["Id"]
        tier = user_info["Tier"]

        try:
            # for earch user, calculate tier
            calculate_user_new_tier(user_id, tier)
        except:
            print("[ERROR] Error calculating new tier for user_id "+user_id)

# --------> Program Starts here

try:
    print("------> Starting TIER Change Calculation <------")
    calculate_users_tier_change()
    print("------> Finished TIER Change Calculation <------")
except Exception as err:
    print("[Error] Error calculate users tier change", err)
    sqlserver_conn.close()

sqlserver_conn.close()
