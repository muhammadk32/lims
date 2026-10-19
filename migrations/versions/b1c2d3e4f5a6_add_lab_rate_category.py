"""add Laboratory.rate_category_id FK

Revision ID: b1c2d3e4f5a6
Revises: d1c178c663c4
Create Date: 2026-10-15 18:40:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'b1c2d3e4f5a6'
down_revision = 'd1c178c663c4'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('laboratories', schema=None) as b:
        b.add_column(sa.Column('rate_category_id', sa.Integer(), nullable=True))
        b.create_index('ix_laboratories_rate_category_id', ['rate_category_id'])
        b.create_foreign_key('fk_laboratories_rate_category_id',
                             'rate_categories', ['rate_category_id'], ['id'])


def downgrade():
    with op.batch_alter_table('laboratories', schema=None) as b:
        b.drop_constraint('fk_laboratories_rate_category_id', type_='foreignkey')
        b.drop_index('ix_laboratories_rate_category_id')
        b.drop_column('rate_category_id')
