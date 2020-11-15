#!/bin/bash

echo $(date)

# Delete flask process if still running from last cron.
flask_pid=$(pgrep -f flask) && kill -9 $flask_pid || echo "No flask process found"

export FLASK_APP=./02_calculate/01_web_api-calc_and_transacts.py

# ------ Start Web API
echo "Starting Web API..."
python3 -m flask run &

# Sleep for 5 seconds until Flask API is up.
sleep 5

echo "Calling Web Api..."
curl localhost:5000

# Sleep for 10 seconds and call tier change.
sleep 10

echo "Starting tier change calculations"

# ------ Call tier change
python3 ./02_calculate/02_tier_change_calc.py