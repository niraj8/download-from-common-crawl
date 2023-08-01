# download-from-common-crawl

## install requirements

```
cd python
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## create .env file

```
cp .env.example .env
```

- update the values in the .env file

## run the script

- Update the query params in main.py
- `python main.py`

## IMPORTANT

Each month CommonCrawl creates a new index that would need to be included in our index

```
python repair_table.py
```
