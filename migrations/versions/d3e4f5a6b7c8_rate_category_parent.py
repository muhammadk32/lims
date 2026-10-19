"""rate_category: parent_rate_category_id + is_standard

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
Create Date: 2026-10-19 14:15:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'd3e4f5a6b7c8'
down_revision = 'c2d3e4f5a6b7'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('rate_categories', schema=None) as b:
        b.add_column(sa.Column('parent_rate_category_id', sa.Integer(), nullable=True))
        b.add_column(sa.Column('is_standard', sa.Boolean(), nullable=False, server_default=sa.text('0')))
        b.create_index('ix_rate_categories_parent', ['parent_rate_category_id'])
        b.create_foreign_key('fk_rate_categories_parent', 'rate_categories',
                             ['parent_rate_category_id'], ['id'])


def downgrade():
    with op.batch_alter_table('rate_categories', schema=None) as b:
        b.drop_constraint('fk_rate_categories_parent', type_='foreignkey')
        b.drop_index('ix_rate_categories_parent')
        b.drop_column('is_standard')
        b.drop_column('parent_rate_category_id')
