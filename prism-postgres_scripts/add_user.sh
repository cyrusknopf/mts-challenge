#!/bin/bash
# Usage:
#   ./insert_team.sh <DB_HOST> <TEAM_NAME> <API_KEY> <POINTS> <PROFIT> [LAST_INTERVAL]
#
# Example:
#   ./insert_team.sh localhost "Alpha Traders" a 950 142.57 "1 hour"

# Check if at least 5 arguments are provided.
if [ "$#" -lt 5 ]; then
    echo "Usage: $0 <DB_HOST> <TEAM_NAME> <API_KEY> <POINTS> <PROFIT> [LAST_INTERVAL]"
    exit 1
fi

DB_HOST="$1"
TEAM_NAME="$2"
API_KEY="$3"
POINTS="$4"
PROFIT="$5"

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
psql -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -U "$DB_USER" -c "$SQL"
