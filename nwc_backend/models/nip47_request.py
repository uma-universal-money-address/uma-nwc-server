# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from typing import Any, Optional
from uuid import UUID, uuid4

from nostr_sdk import ErrorCode, Nip47Error
from sqlalchemy import JSON
from sqlalchemy import Enum as DBEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.orm import Mapped, Session, mapped_column

from nwc_backend.db import UUID as DBUUID
from nwc_backend.db import Column, db
from nwc_backend.models.model_base import ModelBase
from nwc_backend.models.nip47_request_method import Nip47RequestMethod


class Nip47Request(ModelBase):
    __tablename__ = "nip47_request"

    app_connection_id: Mapped[UUID] = Column(
        DBUUID(), ForeignKey("app_connection.id"), nullable=False
    )
    event_id: Mapped[str] = mapped_column(String(length=255), nullable=False)
    method: Mapped[Nip47RequestMethod] = mapped_column(
        DBEnum(Nip47RequestMethod, native_enum=False), nullable=False
    )
    params: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"), nullable=False
    )
    response_event_id: Mapped[Optional[str]] = mapped_column(String(length=255))
    response_result: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql")
    )
    response_error_code: Mapped[Optional[ErrorCode]] = mapped_column(
        DBEnum(ErrorCode, native_enum=False)
    )

    @staticmethod
    async def create_and_save(
        app_connection_id: UUID,
        event_id: str,
        method: Nip47RequestMethod,
        params: Optional[dict[str, Any]],
    ) -> "Nip47Request":
        with Session(db.engine) as db_session:
            request = Nip47Request(
                id=uuid4(),
                app_connection_id=app_connection_id,
                event_id=event_id,
                method=method,
                params=params,
                response_result=None,
                response_event_id=None,
            )
            db_session.add(request)
            db_session.commit()
            return request

    async def update_response_and_save(
        self,
        response_event_id: str,
        response: dict[str, Any] | Nip47Error,
    ) -> None:
        with Session(db.engine) as db_session:
            self.response_event_id = response_event_id
            if isinstance(response, Nip47Error):
                self.response_error_code = response.code
            else:
                self.response_result = response
            db_session.add(self)
            db_session.commit()
