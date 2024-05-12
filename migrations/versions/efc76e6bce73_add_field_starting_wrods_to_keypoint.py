"""Add field starting_wrods to KeyPoint

Revision ID: efc76e6bce73
Revises: d56345f3da21
Create Date: 2024-05-12 21:16:48.616029

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'efc76e6bce73'
down_revision = 'd56345f3da21'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('key_point', schema=None) as batch_op:
        batch_op.add_column(sa.Column('starting_words', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('key_point', schema=None) as batch_op:
        batch_op.drop_column('starting_words')

    # ### end Alembic commands ###
