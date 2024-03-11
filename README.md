# seent

a seer bot history fetching tool

## setup
```
python -m venv venv
. venv/bin/activate
pip install -r requirements.pip
cp .env.example .env
```

Then fill in you api id/hash from my.telegram.com along with your phone number

```python
# this fetches the telegram history
python runner.py
```

```
python app.py
```

after you have the db, you can run the app with `vercel dev` or `python3 src/app.py`

# DB
An example query you might call on to find the green calls and when they were called

```sql
SELECT name || ': ' || strftime('%m-%d %H:%M:%S', date) AS formatted_name_date FROM token_data WHERE ai_degen = 'green' GROUP BY name, date ORDER BY date ASC;
```

get a specific tickers call data
```sql
SELECT * from token_data where name LIKE '%WADDUP%';
```

get the memeability scores ordered by highest to lowest

```sql
select memeability || ' - ' || name from token_data where memeability is not null order by memeability desc;
```
