"""empty message

Revision ID: 9855f72ce6af
Revises: 1745fdb24b5b
Create Date: 2024-03-05 00:03:15.683359

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9855f72ce6af'
down_revision = '1745fdb24b5b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('images', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_name', sa.String(length=128), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('images', schema=None) as batch_op:
        batch_op.drop_column('image_name')

    # ### end Alembic commands ###
