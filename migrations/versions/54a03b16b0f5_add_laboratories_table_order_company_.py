"""add laboratories table + order company fields

Revision ID: 54a03b16b0f5
Revises: 0ae9114c4cfc
Create Date: 2026-10-07 16:58:36.183076

"""
from alembic import op
import sqlalchemy as sa


revision = '54a03b16b0f5'
down_revision = '0ae9114c4cfc'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'laboratories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('contact_person', sa.String(length=120), nullable=True),
        sa.Column('phone', sa.String(length=30), nullable=True),
        sa.Column('email', sa.String(length=120), nullable=True),
        sa.Column('address', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('discount_percent', sa.Float(), nullable=False, server_default='0'),
        sa.Column('commission_percent', sa.Float(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('times_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_laboratories_name', 'laboratories', ['name'], unique=True)

    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('company_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('company_name', sa.String(length=150), nullable=True))
        batch_op.create_index('ix_orders_company_id', ['company_id'], unique=False)
        batch_op.create_foreign_key(
            'fk_orders_company_id', 'laboratories', ['company_id'], ['id']
        )


def downgrade():
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_constraint('fk_orders_company_id', type_='foreignkey')
        batch_op.drop_index('ix_orders_company_id')
        batch_op.drop_column('company_name')
        batch_op.drop_column('company_id')

    op.drop_index('ix_laboratories_name', table_name='laboratories')
    op.drop_table('laboratories')
