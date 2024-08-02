# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved


from sqlalchemy import String

from nwc_backend.db import Column, UUID
from nwc_backend.models.model_base import ModelBase
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Integer, Text, TIMESTAMP


class NWCConnection(ModelBase):
    """
    Represents a connection to the NWC server and the VASP for a specific client app.
    """

    __tablename__ = "nwc_connection"

    user_id = Column(UUID, ForeignKey("user.id"), nullable=False)
    app_name = Column(String(255))
    description = Column(String(255))
    supported_commands = Column(Text)  # Store JSON as string
    connection_expiration = Column(TIMESTAMP(timezone=True))
    max_budget_per_month = Column(Integer)
    long_lived_vasp_token = Column(String(255))
    long_lived_vasp_token_expiration = Column(TIMESTAMP(timezone=True))

    user = relationship("User", back_populates="nwc_connections")
