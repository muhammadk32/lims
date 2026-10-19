"""add RateCategoryDeptRate

Revision ID: e5f6a7b8c9d0
Revises: d3e4f5a6b7c8
Create Date: 2026-10-19 15:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'e5f6a7b8c9d0'
down_revision = 'd3e4f5a6b7c8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('rate_category_dept_rates',
        sa.Column('rate_category_id', sa.Integer(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=False),
        sa.Column('discount_percent', sa.Float(), nullable=False, server_default='0'),
        sa.Column('commission_percent', sa.Float(), nullable=False, server_default='0'),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['rate_category_id'], ['rate_categories.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['department_id'], ['test_categories.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rate_category_id', 'department_id', name='uq_rc_dept'),
    )
    with op.batch_alter_table('rate_category_dept_rates', schema=None) as b:
        b.create_index('ix_rc_dept_rc', ['rate_category_id'])
        b.create_index('ix_rc_dept_dept', ['department_id'])


def downgrade():
    op.drop_table('rate_category_dept_rates')
