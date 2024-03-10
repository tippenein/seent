#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
  export $(cat .env | xargs)
else
  echo ".env file not found"
  exit 1
fi

DUMP_SQL_PATH=dump.sql
TABLE_NAME=token_data

sed -e '/PRAGMA/d' \
    -e 's/BEGIN TRANSACTION;/BEGIN;/d' \
    -e 's/COMMIT;/COMMIT;/' \
    -e 's/ROLLBACK;/ROLLBACK;/' \
    -e 's/CREATE TABLE \"/CREATE TABLE IF NOT EXISTS \"/g' \
    -e 's/INSERT INTO \"/INSERT INTO /g' \
    -e 's/\" VALUES/ VALUES/g' \
    dump.sql > postgres_ready_dump.sql

psql "postgres://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:5432/$POSTGRES_NAME" < postgres_ready_dump.sql

PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<EOF
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