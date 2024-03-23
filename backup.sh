#!/bin/bash

# Get the current date and time in the format of 'YYYYMMDD-HHMMSS'
datetime=$(date +"%Y%m%d-%H%M%S")

# Copy the database file to a new file with the datetime suffix
cp seent.db "db/backups/seent.db.bak.$datetime"
