"""rate_category_tests: add discount_percent + commission_percent

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-10-19 16:30:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'f6a7b8c9d0e1'
down_revision = 'e5f6a7b8c9d0'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('rate_category_tests', schema=None) as b:
        b.add_column(sa.Column('discount_percent', sa.Float(), nullable=True))
        b.add_column(sa.Column('commission_percent', sa.Float(), nullable=True))


def downgrade():
    with op.batch_alter_table('rate_category_tests', schema=None) as b:
        b.drop_column('commission_percent')
        b.drop_column('discount_percent')
