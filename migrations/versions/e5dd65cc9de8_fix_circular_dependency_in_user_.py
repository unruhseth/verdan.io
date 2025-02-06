"""Fix circular dependency in User & PaymentMethod

Revision ID: e5dd65cc9de8
Revises: 
Create Date: 2025-02-05 17:00:47.061888

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5dd65cc9de8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('subdomain', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('subdomain')
    )
    op.create_table('apps',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('device_groups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('ota_updates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('version', sa.String(length=50), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['device_groups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('role', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('subscription_status', sa.String(length=20), nullable=True),
    sa.Column('subscription_type', sa.String(length=10), nullable=True),
    sa.Column('default_payment_method_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
    sa.ForeignKeyConstraint(['default_payment_method_id'], ['payment_method.id'], use_alter=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('payment_method',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('stripe_payment_method_id', sa.String(length=255), nullable=False),
    sa.Column('card_last4', sa.String(length=4), nullable=False),
    sa.Column('card_brand', sa.String(length=50), nullable=False),
    sa.Column('is_default', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('stripe_payment_method_id')
    )
    op.create_table('sim_cards',
    sa.Column('id', sa.String(length=20), nullable=False),
    sa.Column('app_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('iccid', sa.String(length=20), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('extra_data', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['app_id'], ['apps.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('iccid')
    )
    op.create_table('subscription',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('app_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('billing_cycle', sa.String(length=10), nullable=True),
    sa.Column('next_billing_date', sa.DateTime(), nullable=False),
    sa.Column('custom_price', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['app_id'], ['apps.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_apps',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('app_id', sa.Integer(), nullable=False),
    sa.Column('access_level', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['app_id'], ['apps.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('devices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('app_id', sa.Integer(), nullable=False),
    sa.Column('sim_card_id', sa.String(length=20), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('extra_data', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['app_id'], ['apps.id'], ),
    sa.ForeignKeyConstraint(['sim_card_id'], ['sim_cards.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('invoice',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('payment_method_id', sa.Integer(), nullable=True),
    sa.Column('stripe_invoice_id', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['payment_method_id'], ['payment_method.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('stripe_invoice_id')
    )
    op.create_table('device_group_association',
    sa.Column('device_id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
    sa.ForeignKeyConstraint(['group_id'], ['device_groups.id'], ),
    sa.PrimaryKeyConstraint('device_id', 'group_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('device_group_association')
    op.drop_table('invoice')
    op.drop_table('devices')
    op.drop_table('user_apps')
    op.drop_table('subscription')
    op.drop_table('sim_cards')
    op.drop_table('payment_method')
    op.drop_table('users')
    op.drop_table('ota_updates')
    op.drop_table('device_groups')
    op.drop_table('apps')
    op.drop_table('account')
    # ### end Alembic commands ###
