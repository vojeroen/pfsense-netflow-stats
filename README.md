# pfSense NetFlow stats

## Installation

A PostgreSQL database is required. The default config uses database `ipfix`, username `ipfix` and password `ipfix` on `localhost`. This can be changed in `alembic.ini` and `models/__init__.py`. The database `ipfix` needs to have the extension `uuid-ossp` enabled:
```postgresql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
``` 

Create a virtual environment based on `requirements.txt`.

To initialize the database:
```shell script
PYTHONPATH=. alembic upgrade head
```

To start:
```shell script
python collect.py
python parse.py
python visual.py
```

On a regular basis (e.g. every minute):
```shell script
python summary.py
```

By default the service listens on all interfaces on port 9000.
 