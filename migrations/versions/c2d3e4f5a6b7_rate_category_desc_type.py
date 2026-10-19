"""rate_category: add description, rate_type

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-10-19 13:10:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'c2d3e4f5a6b7'
down_revision = 'b1c2d3e4f5a6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('rate_categories', schema=None) as b:
        b.add_column(sa.Column('description', sa.String(length=255), nullable=True))
        b.add_column(sa.Column('rate_type', sa.String(length=20), nullable=True))


def downgrade():
    with op.batch_alter_table('rate_categories', schema=None) as b:
        b.drop_column('rate_type')
        b.drop_column('description')
