"""add unique to user.nostr_pubkey

Revision ID: b959cba00f93
Revises: 6425881f2240
Create Date: 2024-07-29 16:43:05.385892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b959cba00f93'
down_revision: Union[str, None] = '6425881f2240'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('app_connection', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['nostr_pubkey'])

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('app_connection', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    # ### end Alembic commands ###