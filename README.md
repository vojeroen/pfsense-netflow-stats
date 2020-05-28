# pfSense NetFlow stats

## Installation

A PostgreSQL database is required. The default config uses database `ipfix`, username `ipfix` and password `ipfix` on `localhost`. This can be changed in `alembic.ini` and `models/__init__.py`. 

To initialize the database:
```shell script
PYTHONPATH=. alembic upgrade head
```

To start:
```shell script
python ipfix.py
```

By default the service listens on all interfaces on port 9000.
 