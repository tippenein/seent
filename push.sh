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
    -e 's/CREATE TABLE \"/CREATE TABLE IF NOT EXISTS \"/g' \
    -e 's/INSERT INTO \"/INSERT INTO /g' \
    -e 's/\" VALUES/ VALUES/g' \
    "$DUMP_SQL_PATH" > postgres_ready_dump.sql

# Execute the SQL within a transaction in PostgreSQL
PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_NAME" <<EOF
BEGIN;
DROP TABLE IF EXISTS $TABLE_NAME;
\i postgres_ready_dump.sql
COMMIT;
EOF

# Check if the transaction was successful
if [ $? -eq 0 ]; then
  echo "Table replaced and data imported successfully."
else
  echo "Failed to replace table and import data."
  exit 1
fi