# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from uuid import uuid4

from quart.app import QuartClient
from sqlalchemy.orm import Session

from nwc_backend.db import db
from nwc_backend.models.user import User


async def test_user_model(test_client: QuartClient) -> None:
    uma_address = "$alice@uma.me"

    # test creation
    with Session(db.engine) as db_session:
        user = User(id=uuid4(), vasp_user_id=str(uuid4()), uma_address=uma_address)
        db_session.add(user)
        db_session.commit()

    # test update
    with Session(db.engine) as db_session:
        user = db_session.query(User).filter_by(uma_address=uma_address).first()
        assert user

        uma_address = "$bob@uma.me"
        user.uma_address = uma_address
        db_session.commit()

    with Session(db.engine) as db_session:
        user = db_session.query(User).filter_by(uma_address=uma_address).first()
        assert user
