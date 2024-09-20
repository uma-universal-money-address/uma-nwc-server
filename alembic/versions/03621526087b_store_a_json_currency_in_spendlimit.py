"""store a json currency in SpendLimit

Revision ID: 03621526087b
Revises: 5d76da39d538
Create Date: 2024-09-20 00:06:50.361635

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op
from nwc_backend.models.spending_limit import DBCurrency

# revision identifiers, used by Alembic.
revision: str = "03621526087b"
down_revision: Union[str, None] = "5d76da39d538"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("spending_limit", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "currency",
                DBCurrency(),
                nullable=False,
            )
        )
        batch_op.drop_column("currency_code")

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("spending_limit", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("currency_code", sa.VARCHAR(length=3), nullable=False)
        )
        batch_op.drop_column("currency")

    # ### end Alembic commands ###
