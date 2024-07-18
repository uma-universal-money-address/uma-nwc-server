# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from sqlalchemy import create_engine

class SQLAlchemyDB:
    _engine = None

    def init_app(self, app):
        self._engine = create_engine(app.config["DATABASE_URI"])

    @property
    def engine(self):
        assert self._engine
        return self._engine


db = SQLAlchemyDB()
