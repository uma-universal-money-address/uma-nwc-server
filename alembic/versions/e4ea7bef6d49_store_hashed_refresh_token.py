"""Store hashed refresh token

Revision ID: e4ea7bef6d49
Revises: a15389988245
Create Date: 2024-09-29 10:35:42.783210

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e4ea7bef6d49"
down_revision: Union[str, None] = "a15389988245"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("nwc_connection", schema=None) as batch_op:
        batch_op.drop_constraint("nwc_connection_unique_refresh_token", type_="unique")
        batch_op.alter_column("refresh_token", new_column_name="hashed_refresh_token")
        batch_op.create_unique_constraint(
            "nwc_connection_unique_hashed_refresh_token", ["hashed_refresh_token"]
        )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("nwc_connection", schema=None) as batch_op:
        batch_op.drop_constraint(
            "nwc_connection_unique_hashed_refresh_token", type_="unique"
        )
        batch_op.alter_column("hashed_refresh_token", new_column_name="refresh_token")
        batch_op.create_unique_constraint(
            "nwc_connection_unique_refresh_token", ["refresh_token"]
        )

    # ### end Alembic commands ###
