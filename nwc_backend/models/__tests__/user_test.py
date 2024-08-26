# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from uuid import uuid4

from quart.app import QuartClient

from nwc_backend.db import db
from nwc_backend.models.user import User


async def test_user_model(test_client: QuartClient) -> None:
    uma_address = "$alice@uma.me"

    # test creation
    async with test_client.app.app_context():
        user = User(id=uuid4(), vasp_user_id=str(uuid4()), uma_address=uma_address)
        db.session.add(user)
        db.session.commit()

    # test update
    async with test_client.app.app_context():
        user = db.session.query(User).filter_by(uma_address=uma_address).first()
        assert user

        uma_address = "$bob@uma.me"
        user.uma_address = uma_address
        db.session.commit()

    async with test_client.app.app_context():
        user = db.session.query(User).filter_by(uma_address=uma_address).first()
        assert user
