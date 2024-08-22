# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from secrets import token_hex
from uuid import uuid4

from quart.app import QuartClient
from sqlalchemy.orm import Session

from nwc_backend.db import db
from nwc_backend.models.__tests__.model_examples import create_app_connection
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.models.nip47_request_method import Nip47RequestMethod


async def test_nip47_request_model(test_client: QuartClient) -> None:
    id = uuid4()
    event_id = token_hex()
    method = Nip47RequestMethod.PAY_INVOICE
    params = {
        "invoice": "lnbcrt1pjrsa37pp50geu5vxkzn4ddc4hmfkz9x308tw9lrrqtktz2hpm0rccjyhcyp5qdqh2d68yetpd45kueeqv3jk6mccqzpgxq9z0rgqsp5ge2rdw0tzvakxslmtvfmqf2fr7eucg9ughps5vdvp6fm2utk20rs9q8pqqqssqjs3k4nzrzg2nu9slu9c3srv2ae8v69ge097q9seukyw2nger8arj93m6erz8u657hfdzztfmc55wjjm9k337krl00fyw6s9nnwaafaspcqp2uv"
    }
    response_event_id = token_hex()
    response_result = {
        "preimage": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
    with Session(db.engine) as db_session:
        app_connection_id = create_app_connection(db_session).id
        nip47_request = Nip47Request(
            id=id,
            app_connection_id=app_connection_id,
            event_id=event_id,
            method=method,
            params=params,
            response_event_id=response_event_id,
            response_result=response_result,
        )
        db_session.add(nip47_request)
        db_session.commit()

    with Session(db.engine) as db_session:
        nip47_request = db_session.query(Nip47Request).get(id)
        assert isinstance(nip47_request, Nip47Request)
        assert nip47_request.event_id == event_id
        assert nip47_request.app_connection_id == app_connection_id
        assert nip47_request.method == method
        assert nip47_request.params == params
        assert nip47_request.response_event_id == response_event_id
        assert nip47_request.response_result == response_result
