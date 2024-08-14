from quart import Quart
from nwc_backend import create_app
from a2wsgi import ASGIMiddleware

app: Quart = create_app()
wsgi = ASGIMiddleware(app, wait_time=5)  # pyre-ignore[6]
