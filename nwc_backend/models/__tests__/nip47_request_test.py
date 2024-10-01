from secrets import token_hex
from uuid import uuid4

from quart.app import QuartClient

from nwc_backend.db import db
from nwc_backend.models.__tests__.model_examples import create_nwc_connection
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

    async with test_client.app.app_context():
        nwc_connection_id = (await create_nwc_connection()).id
        nip47_request = Nip47Request(
            id=id,
            nwc_connection_id=nwc_connection_id,
            event_id=event_id,
            method=method,
            params=params,
            response_event_id=response_event_id,
            response_result=response_result,
        )
        db.session.add(nip47_request)
        await db.session.commit()

    async with test_client.app.app_context():
        nip47_request = await db.session.get_one(Nip47Request, id)
        assert nip47_request.event_id == event_id
        assert nip47_request.nwc_connection_id == nwc_connection_id
        assert nip47_request.method == method
        assert nip47_request.params == params
        assert nip47_request.response_event_id == response_event_id
        assert nip47_request.response_result == response_result
