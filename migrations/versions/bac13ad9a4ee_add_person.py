"""add Person

Revision ID: bac13ad9a4ee
Revises: 7d3c75cbbfab
Create Date: 2024-09-14 15:38:30.501063

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bac13ad9a4ee'
down_revision = '7d3c75cbbfab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reword', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))

    with op.batch_alter_table('user_points', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_points', schema=None) as batch_op:
        batch_op.drop_column('user_id')

    with op.batch_alter_table('reword', schema=None) as batch_op:
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###
