#!/bin/bash
# Usage:
#   ./insert_team.sh <DB_HOST> <TEAM_NAME>  <POINTS> <PROFIT> [LAST_INTERVAL]
#
# Example:
#   ./insert_team.sh localhost "Alpha Traders" 950 142.57 "1 hour"

# Check if at least 5 arguments are provided.
if [ "$#" -lt 4 ]; then
    echo "Usage: $0 <DB_HOST> <TEAM_NAME> <POINTS> <PROFIT> [LAST_INTERVAL]"
    exit 1
fi

DB_HOST="$1"
TEAM_NAME="$2"
API_KEY=`echo $((1 + $RANDOM )) | md5sum - | cut -d' ' -f1`
POINTS="$3"
PROFIT="$4"

# Optional parameter: last_interval for last_submission_time; default is "1 hour"
LAST_INTERVAL="${6:-1 hour}"

# Fixed database parameters
DB_PORT=5432
DB_NAME="prism"
DB_USER="postgres"

# Construct the SQL command.
SQL="INSERT INTO teams (team_name, api_key, points, profit, last_submission_time)
VALUES ('$TEAM_NAME', '$API_KEY', $POINTS, $PROFIT, NOW() - INTERVAL '$LAST_INTERVAL');"

echo "Executing SQL command:"
echo "$SQL"

# Run the SQL command using psql.
PGPASSWORD='l??pT-87pBqE2hN9-zY/)' psql -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -U "$DB_USER" -c "$SQL"
