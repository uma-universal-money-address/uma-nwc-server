# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from typing import Any, Optional
from uuid import UUID

from nostr_sdk import ErrorCode
from sqlalchemy import JSON
from sqlalchemy import Enum as DBEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from nwc_backend.db import UUID as DBUUID
from nwc_backend.db import Column
from nwc_backend.event_handlers.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.model_base import ModelBase


class Nip47Request(ModelBase):
    __tablename__ = "nip47_request"

    app_connection_id: Mapped[UUID] = Column(
        DBUUID(), ForeignKey("app_connection.id"), nullable=False
    )
    event_id: Mapped[str] = mapped_column(String(length=255), nullable=False)
    method: Mapped[Nip47RequestMethod] = mapped_column(
        DBEnum(Nip47RequestMethod, native_enum=False), nullable=False
    )
    params: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql")
    )
    response_event_id: Mapped[Optional[str]] = mapped_column(String(length=255))
    response_result: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql")
    )
    response_error_code: Mapped[Optional[ErrorCode]] = mapped_column(
        DBEnum(ErrorCode, native_enum=False)
    )
