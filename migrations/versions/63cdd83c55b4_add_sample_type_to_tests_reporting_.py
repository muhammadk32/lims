"""add sample_type to tests, reporting/sample/company on order_items

Revision ID: 63cdd83c55b4
Revises: 99468210c034
Create Date: 2026-10-09 14:10:33.168xxx

"""
from alembic import op
import sqlalchemy as sa


revision = '63cdd83c55b4'
down_revision = '99468210c034'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('tests', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sample_type', sa.String(length=120), nullable=True))

    with op.batch_alter_table('order_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reporting_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('sample_type', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('company_rate', sa.Float(), nullable=True))


def downgrade():
    with op.batch_alter_table('order_items', schema=None) as batch_op:
        batch_op.drop_column('company_rate')
        batch_op.drop_column('sample_type')
        batch_op.drop_column('reporting_date')

    with op.batch_alter_table('tests', schema=None) as batch_op:
        batch_op.drop_column('sample_type')
