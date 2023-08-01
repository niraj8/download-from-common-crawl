# download-from-common-crawl

## install requirements

```shell
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

- create index in Athena using [create_ccindex.athena](./create_ccindex.athena)

## create .env file

```shell
cp .env.example .env
```

- update the values in the .env file

## run the script

- Update the query params in main.py
- `python python/main.py`

## IMPORTANT

Each month CommonCrawl creates a new index that would need to be included in our index

```shell
python python/repair_table.py
```
