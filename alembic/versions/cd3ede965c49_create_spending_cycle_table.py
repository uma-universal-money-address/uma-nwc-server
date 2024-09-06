"""create spending_cycle table

Revision ID: cd3ede965c49
Revises: ed85eb9c966f
Create Date: 2024-09-06 10:11:23.479619

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op
from nwc_backend.db import UUID, DateTime

# revision identifiers, used by Alembic.
revision: str = "cd3ede965c49"
down_revision: Union[str, None] = "ed85eb9c966f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "spending_cycle",
        sa.Column("spending_limit_id", UUID(), nullable=False),
        sa.Column("limit_currency", sa.String(length=3), nullable=False),
        sa.Column("limit_amount", sa.BigInteger(), nullable=False),
        sa.Column("start_time", DateTime(), nullable=False),
        sa.Column("end_time", DateTime(), nullable=True),
        sa.Column("total_spent", sa.BigInteger(), nullable=False),
        sa.Column("total_spent_on_hold", sa.BigInteger(), nullable=False),
        sa.Column("id", UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["spending_limit_id"],
            ["spending_limit.id"],
            name="spending_cycle_spending_limit_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("spending_cycle", schema=None) as batch_op:
        batch_op.create_index(
            "spending_cycle_spending_limit_id_start_time_unique_idx",
            ["spending_limit_id", "start_time"],
            unique=True,
        )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("spending_cycle", schema=None) as batch_op:
        batch_op.drop_index("spending_cycle_spending_limit_id_start_time_unique_idx")

    op.drop_table("spending_cycle")
    # ### end Alembic commands ###