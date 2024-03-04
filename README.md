# seent

a seer bot history fetching tool

## setup
```
cp .env.example .env
```

Then fill in you api id/hash from my.telegram.com along with your phone number

```python
python3 main.py
```

An example query you might call on to find the green calls and when they were called

```sql
SELECT name || ': ' || strftime('%m-%d %H:%M:%S', date) AS formatted_name_date FROM token_data WHERE ai_degen = 'green' GROUP BY name, date ORDER BY date ASC;
```