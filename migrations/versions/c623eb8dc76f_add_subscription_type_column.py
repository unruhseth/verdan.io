"""Add subscription_type column

Revision ID: c623eb8dc76f
Revises: e5dd65cc9de8
Create Date: 2025-02-05 18:45:51.735545

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c623eb8dc76f'
down_revision = 'e5dd65cc9de8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('subscription', schema=None) as batch_op:
        batch_op.add_column(sa.Column('subscription_type', sa.String(length=20), nullable=False))

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'payment_method', ['default_payment_method_id'], ['id'], use_alter=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('subscription', schema=None) as batch_op:
        batch_op.drop_column('subscription_type')

    # ### end Alembic commands ###
