# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from uuid import uuid4

from quart.app import QuartClient
from sqlalchemy.orm import Session

from nwc_backend.db import db
from nwc_backend.models.__tests__.model_examples import create_client_app, create_user
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.nwc_connection import NWCConnection


async def test_nwc_connection_model(test_client: QuartClient) -> None:
    id = uuid4()
    with Session(db.engine) as db_session:
        user_id = create_user(db_session).id
        client_app_id = create_client_app(db_session).id
        nwc_connection = NWCConnection(
            id=id,
            user_id=user_id,
            client_app_id=client_app_id,
            supported_commands=[
                Nip47RequestMethod.MAKE_INVOICE.value,
                Nip47RequestMethod.PAY_INVOICE.value,
            ],
        )
        db_session.add(nwc_connection)
        db_session.commit()

    with Session(db.engine) as db_session:
        nwc_connection = db_session.query(NWCConnection).get(id)
        assert isinstance(nwc_connection, NWCConnection)
        assert nwc_connection.user.id == user_id
        assert nwc_connection.client_app.id == client_app_id
        assert nwc_connection.has_command_permission(Nip47RequestMethod.MAKE_INVOICE)
        assert not nwc_connection.has_command_permission(Nip47RequestMethod.FETCH_QUOTE)
