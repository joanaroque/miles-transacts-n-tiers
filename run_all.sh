#! /bin/bash

echo "******************"

echo "01 - Recreating mysql tickets table."
./01_recreate_mysql_table.sh
echo "******************"


echo "02 - Generating dummy tickets"
./02_generate_dummy_tickets.sh
echo "******************"

echo "03 - Running web api to create TX and tier changes."
./03_run_web_api.sh
echo "******************"


echo "FINISH"