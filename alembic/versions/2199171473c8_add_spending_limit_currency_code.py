"""add spending limit currency code

Revision ID: 2199171473c8
Revises: f5ad7f32c91a
Create Date: 2024-08-26 17:14:06.709452

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2199171473c8"
down_revision: Union[str, None] = "f5ad7f32c91a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("nwc_connection", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("spending_limit_amount", sa.BigInteger(), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "spending_limit_currency_code", sa.String(length=3), nullable=True
            )
        )
        batch_op.add_column(
            sa.Column(
                "spending_limit_frequency",
                sa.Enum(
                    "DAILY",
                    "WEEKLY",
                    "MONTHLY",
                    "YEARLY",
                    "NONE",
                    name="spendinglimitfrequency",
                    native_enum=False,
                ),
                nullable=True,
            )
        )
        batch_op.drop_column("max_budget_per_month")

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("nwc_connection", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("max_budget_per_month", sa.INTEGER(), nullable=True)
        )
        batch_op.drop_column("spending_limit_frequency")
        batch_op.drop_column("spending_limit_currency_code")
        batch_op.drop_column("spending_limit_amount")

    # ### end Alembic commands ###
