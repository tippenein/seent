DB_NAME:=seent.db
dump:
	sqlite3 seent.db .dump > dump.sql

backup:
	./backup.sh

run:
	./run.sh

create: backup scrape
	

scrape:
	./scrape.sh

test:
	python3 -m unittest test_parser.py
