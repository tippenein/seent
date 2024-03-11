DB_NAME:=seent.db
dump:
	sqlite3 seent.db .dump > dump.sql

backup:
	./backup.sh

run:
	python3 app.py

create: backup scrape
	

scrape:
	./run.sh

test:
	python3 -m unittest test_parser.py
