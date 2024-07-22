# uma-nwc-server

A Nostr Wallet Connect server for UMA VASPs.

Built using Quart + OpenAPI + SQLAlchemy + Alembic

To run quart server locally -

- pipenv shell -> activate pipenv
- create instance/nwc.sqlite if it doesn't already exists
- alembic upgrade head -> run migrations on db
- export QUART_APP=nwc_backend
- quart run
