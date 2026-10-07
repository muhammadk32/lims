"""add pcr_templates table

Revision ID: 0ae9114c4cfc
Revises: c90faa23e01a
Create Date: 2026-10-07 12:47:23.692492

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ae9114c4cfc'
down_revision = 'c90faa23e01a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'pcr_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('test_id', sa.Integer(), nullable=False),
        sa.Column('methodology_html', sa.Text(), nullable=True),
        sa.Column('suggestion_html', sa.Text(), nullable=True),
        sa.Column('interpretation_html', sa.Text(), nullable=True),
        sa.Column('comments_html', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['test_id'], ['tests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_pcr_templates_test_id',
        'pcr_templates',
        ['test_id'],
        unique=True,
    )


def downgrade():
    op.drop_index('ix_pcr_templates_test_id', table_name='pcr_templates')
    op.drop_table('pcr_templates')
