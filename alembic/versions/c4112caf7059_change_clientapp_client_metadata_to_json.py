"""change ClientApp.client_metadata to json

Revision ID: c4112caf7059
Revises: b53591e6efed
Create Date: 2024-08-21 10:26:57.388563

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql.json import JSONB

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c4112caf7059"
down_revision: Union[str, None] = "b53591e6efed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("client_app", schema=None) as batch_op:
        batch_op.alter_column(
            "client_metadata",
            existing_type=sa.TEXT(),
            type_=sa.JSON().with_variant(JSONB(astext_type=sa.Text()), "postgresql"),
            existing_nullable=True,
        )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("client_app", schema=None) as batch_op:
        batch_op.alter_column(
            "client_metadata",
            existing_type=sa.JSON().with_variant(
                JSONB(astext_type=sa.Text()), "postgresql"
            ),
            type_=sa.TEXT(),
            existing_nullable=True,
        )

    # ### end Alembic commands ###
