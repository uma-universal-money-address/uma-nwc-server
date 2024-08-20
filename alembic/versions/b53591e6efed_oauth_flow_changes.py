"""Oauth flow changes

Revision ID: b53591e6efed
Revises: 0fc63b5c0f6c
Create Date: 2024-08-19 16:21:25.872152

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from nwc_backend.db import UUID


# revision identifiers, used by Alembic.
revision: str = "b53591e6efed"
down_revision: Union[str, None] = "0fc63b5c0f6c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("app_connection", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("client_id", sa.String(length=255), nullable=False)
        )
        batch_op.add_column(sa.Column("user_id", UUID(), nullable=False))
        batch_op.add_column(
            sa.Column("authorization_code", sa.String(length=255), nullable=False)
        )
        batch_op.add_column(
            sa.Column("access_token_expires_at", sa.Integer(), nullable=False)
        )
        batch_op.add_column(
            sa.Column("refresh_token_expires_at", sa.Integer(), nullable=False)
        )
        batch_op.add_column(
            sa.Column("authorization_code_expires_at", sa.Integer(), nullable=False)
        )
        batch_op.add_column(sa.Column("revoked", sa.Boolean(), nullable=False))
        batch_op.create_unique_constraint(
            "unique_authorization_code", ["authorization_code"]
        )
        batch_op.create_unique_constraint("unique_client_id", ["client_id"])
        batch_op.create_foreign_key(
            "app_connection_user_fk", "user", ["user_id"], ["id"]
        )
        batch_op.drop_column("connection_expiration")

    with op.batch_alter_table("nwc_connection", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("connection_expires_at", sa.Integer(), nullable=False)
        )
        batch_op.drop_column("connection_expiration")

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("nwc_connection", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("connection_expiration", sa.DATETIME(), nullable=False)
        )
        batch_op.drop_column("connection_expires_at")

    with op.batch_alter_table("app_connection", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("connection_expiration", sa.DATETIME(), nullable=False)
        )
        batch_op.drop_constraint("app_connection_user_fk", type_="foreignkey")
        batch_op.drop_constraint("unique_authorization_code", type_="unique")
        batch_op.drop_constraint("unique_client_id", type_="unique")
        batch_op.drop_column("revoked")
        batch_op.drop_column("authorization_code_expires_at")
        batch_op.drop_column("refresh_token_expires_at")
        batch_op.drop_column("access_token_expires_at")
        batch_op.drop_column("authorization_code")
        batch_op.drop_column("user_id")
        batch_op.drop_column("client_id")

    # ### end Alembic commands ###
