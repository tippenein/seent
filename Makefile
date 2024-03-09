DB_NAME:=seent.db
dump:
	sqlite3 "${DB_NAME}" ".output token_data.sql" ".dump token_data"

backup:
	./backup.sh

run:
	python3 app.py

create: backup scrape
	

scrape:
	./run.sh
