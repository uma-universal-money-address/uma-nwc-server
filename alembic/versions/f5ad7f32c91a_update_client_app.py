"""Update client app

Revision ID: f5ad7f32c91a
Revises: 10ffe99e7310
Create Date: 2024-08-23 15:27:43.947148

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql.json import JSONB

# revision identifiers, used by Alembic.
revision: str = "f5ad7f32c91a"
down_revision: Union[str, None] = "10ffe99e7310"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("app_connection", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "status",
                sa.Enum(
                    "ACTIVE",
                    "INACTIVE",
                    "EXPIRED",
                    "REVOKED",
                    name="appconnectionstatus",
                    native_enum=False,
                ),
                nullable=False,
            )
        )
        batch_op.create_index(
            "app_connection_nwc_connection_unique_idx",
            ["nwc_connection_id"],
            unique=True,
            postgresql_where=sa.text("status = 'ACTIVE'"),
            sqlite_where=sa.text("status = 'ACTIVE'"),
        )
        batch_op.drop_column("revoked")

    with op.batch_alter_table("client_app", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("display_name", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(
            sa.Column("image_url", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "verification_status",
                sa.Enum(
                    "VERIFIED", "INVALID", "UNKNOWN", name="nip05verificationstatus"
                ),
                nullable=True,
            )
        )
        batch_op.alter_column(
            "app_name", existing_type=sa.VARCHAR(length=255), nullable=True
        )
        batch_op.drop_column("client_metadata")
        batch_op.drop_column("description")

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("client_app", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("description", sa.VARCHAR(length=255), nullable=False)
        )
        batch_op.add_column(
            sa.Column(
                "client_metadata",
                sa.JSON().with_variant(JSONB(astext_type=sa.Text()), "postgresql"),
                nullable=True,
            )
        )
        batch_op.alter_column(
            "app_name", existing_type=sa.VARCHAR(length=255), nullable=False
        )
        batch_op.drop_column("verification_status")
        batch_op.drop_column("image_url")
        batch_op.drop_column("display_name")

    with op.batch_alter_table("app_connection", schema=None) as batch_op:
        batch_op.add_column(sa.Column("revoked", sa.BOOLEAN(), nullable=False))
        batch_op.drop_index(
            "app_connection_nwc_connection_unique_idx",
            postgresql_where=sa.text("status = 'ACTIVE'"),
            sqlite_where=sa.text("status = 'ACTIVE'"),
        )
        batch_op.drop_column("status")

    # ### end Alembic commands ###