# uma-nwc-server

A Nostr Wallet Connect server for UMA VASPs.

Built using Quart + OpenAPI + SQLAlchemy + Alembic

## Run the quart server locally

Create a `.quartenv` file:

```bash
QUART_DEBUG=True
QUART_RUN_PORT=5000
QUART_ENV=development
```

Install dependencies:

```bash
pipenv install -d
```

Create the db file if it doesn't already exist:

```bash
mkdir instance
touch instance/nwc.sqlite
```

Run migrations on the db:

```bash
QUART_APP=nwc_backend QUART_CONFIG="configs/local_dev.py" pipenv run alembic upgrade head
```

Run the backend:

```bash
QUART_APP=nwc_backend QUART_CONFIG="configs/local_dev.py" pipenv run quart run
```

Alternatively you could just run the `run_backend.sh` script which sets all the needed env variables for you

## Run black

We use `black` to format python files.

```bash
pipenv run black .
```
