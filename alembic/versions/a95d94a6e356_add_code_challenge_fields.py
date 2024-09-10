"""Add code challenge fields

Revision ID: a95d94a6e356
Revises: 2c83a1c59b75
Create Date: 2024-09-12 13:37:33.306150

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a95d94a6e356"
down_revision: Union[str, None] = "2c83a1c59b75"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("app_connection", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "redirect_uri",
                sa.String(length=1024),
                nullable=False,
                server_default="",
            )
        )
        batch_op.add_column(
            sa.Column(
                "code_challenge",
                sa.String(length=1024),
                nullable=False,
                server_default="",
            )
        )
        batch_op.add_column(
            sa.Column(
                "code_challenge_method",
                sa.String(length=255),
                nullable=False,
                server_default="",
            )
        )
        batch_op.alter_column(
            "authorization_code",
            existing_type=sa.VARCHAR(length=255),
            type_=sa.String(length=1024),
            existing_nullable=False,
        )

    # ### end Alembic commands ###


def downgrade() -> None:
    with op.batch_alter_table("app_connection", schema=None) as batch_op:
        batch_op.alter_column(
            "authorization_code",
            existing_type=sa.String(length=1024),
            type_=sa.VARCHAR(length=255),
            existing_nullable=False,
        )
        batch_op.drop_column("code_challenge_method")
        batch_op.drop_column("code_challenge")
        batch_op.drop_column("redirect_uri")

    # ### end Alembic commands ###
