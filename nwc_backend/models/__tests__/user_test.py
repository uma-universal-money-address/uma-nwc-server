from uuid import uuid4

from quart.app import QuartClient

from nwc_backend.db import db
from nwc_backend.models.user import User


async def test_user_model(test_client: QuartClient) -> None:
    vasp_user_id = str(uuid4())
    uma_address = "$alice@uma.me"

    # test creation
    async with test_client.app.app_context():
        user = User(id=uuid4(), vasp_user_id=vasp_user_id, uma_address=uma_address)
        db.session.add(user)
        await db.session.commit()

    # test update
    async with test_client.app.app_context():
        user = await User.from_vasp_user_id(vasp_user_id)
        assert user
        assert user.uma_address == uma_address

        uma_address = "$bob@uma.me"
        user.uma_address = uma_address
        await db.session.commit()

    async with test_client.app.app_context():
        user = await User.from_vasp_user_id(vasp_user_id)
        assert user
        assert user.uma_address == uma_address
