# quart environment variables
export QUART_CONFIG=${NWC_QUART_CONFIG:-"configs/local_dev.py"}
export QUART_APP=nwc_backend
export QUART_ENV=development
export QUART_DEBUG=True
export QUART_RUN_PORT=8080

pipenv run quart run