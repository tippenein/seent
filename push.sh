#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo ".env file not found"
  exit 1
fi

DUMP_SQL_PATH=dump.sql
TABLE_NAME=token_data

# Prepare the SQLite dump for PostgreSQL
sed -e '/PRAGMA/d' \
    -e '/BEGIN TRANSACTION;/d' \
    -e '/COMMIT;/d' \
    -e '/ROLLBACK;/d' \
    -e 's/integer/bigint/g' \
    -e 's/CREATE TABLE \"/CREATE TABLE IF NOT EXISTS \"/g' \
    -e 's/INSERT INTO \"/INSERT INTO /g' \
    -e 's/\" VALUES/ VALUES/g' \
    "$DUMP_SQL_PATH" > postgres_ready_dump.sql

echo "pushing to db at $POSTGRES_HOST"
echo "$POSTGRES_HOST"
echo "$POSTGRES_USER"
echo "$POSTGRES_DBNAME"
echo "$POSTGRES_PORT"
# Execute the SQL within a transaction in PostgreSQL
PGPASSWORD=$POSTGRES_PASSWORD psql "sslmode=require \
  host=$POSTGRES_HOST \
  user=$POSTGRES_USER \
  dbname=$POSTGRES_DBNAME \
  port=$POSTGRES_PORT" \
  -v ON_ERROR_STOP=1 \
  --echo-errors <<EOF
BEGIN;
DROP TABLE IF EXISTS $TABLE_NAME;
\i postgres_ready_dump.sql
\i db/indexes.sql
COMMIT;
EOF

# Check if the transaction was successful
if [ $? -eq 0 ]; then
  echo "Table replaced and data imported successfully."
else
  echo "Failed to replace table and import data."
  exit 1
fi
