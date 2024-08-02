# quart environment variables
export QUART_CONFIG="configs/local_dev.py"
export QUART_APP=nwc_backend
export QUART_ENV=development
export QUART_DEBUG=True
export QUART_RUN_PORT=5000

# nostr environment variables
export NOSTR_PRIVKEY=$(openssl rand -hex 32)
export RELAY="wss://relay.getalby.com/v1" 

pipenv run quart run