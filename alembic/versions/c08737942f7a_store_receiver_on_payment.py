"""store receiver on payment

Revision ID: c08737942f7a
Revises: b5c2515e5fd5
Create Date: 2024-09-20 21:27:37.830408

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c08737942f7a"
down_revision: Union[str, None] = "b5c2515e5fd5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("outgoing_payment", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("receiver", sa.String(length=10240), nullable=False)
        )
        batch_op.add_column(
            sa.Column(
                "receiver_type",
                sa.Enum(
                    "LUD16",
                    "BOLT12",
                    "BOLT11",
                    "NODE_PUBKEY",
                    name="receivingaddresstype",
                    native_enum=False,
                ),
                nullable=False,
            )
        )

    with op.batch_alter_table("payment_quote", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("receiver_address", sa.String(length=200), nullable=False)
        )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("payment_quote", schema=None) as batch_op:
        batch_op.drop_column("receiver_address")

    with op.batch_alter_table("outgoing_payment", schema=None) as batch_op:
        batch_op.drop_column("receiver_type")
        batch_op.drop_column("receiver")

    # ### end Alembic commands ###
