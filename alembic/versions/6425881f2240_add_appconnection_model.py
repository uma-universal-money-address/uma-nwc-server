"""Add AppConnection model

Revision ID: 6425881f2240
Revises: 7ca25213a1a8
Create Date: 2024-07-29 13:18:17.020112

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from nwc_backend.db import UUID


# revision identifiers, used by Alembic.
revision: str = "6425881f2240"
down_revision: Union[str, None] = "7ca25213a1a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "app_connection",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("app_name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("nostr_pubkey", sa.String(length=255), nullable=True),
        sa.Column("required_commands", sa.Text(), nullable=True),
        sa.Column("optional_commands", sa.Text(), nullable=True),
        sa.Column("max_budget_per_month", sa.Integer(), nullable=True),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("long_lived_vasp_token", sa.String(length=255), nullable=True),
        sa.Column("id", UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("email", sa.String(length=255), nullable=False))
        batch_op.add_column(
            sa.Column("access_token", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(
            sa.Column("refresh_token", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("(CURRENT_TIMESTAMP)"),
                nullable=True,
            )
        )
        batch_op.create_unique_constraint("unique_email", ["email"])

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_constraint("unique_email", type_="unique")
        batch_op.drop_column("updated_at")
        batch_op.drop_column("created_at")
        batch_op.drop_column("refresh_token")
        batch_op.drop_column("access_token")
        batch_op.drop_column("email")

    op.drop_table("app_connection")
    # ### end Alembic commands ###
