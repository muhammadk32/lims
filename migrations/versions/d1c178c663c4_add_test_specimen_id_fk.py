"""add Test.specimen_id FK

Revision ID: d1c178c663c4
Revises: fb85a11c9638
Create Date: 2026-10-15 17:39:48.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'd1c178c663c4'
down_revision = 'fb85a11c9638'
branch_labels = None
depends_on = None


def upgrade():
    # SQLite doesn't support adding FK constraints on existing tables via ALTER.
    # batch_alter_table recreates the table with the new FK.
    with op.batch_alter_table('tests', schema=None) as b:
        b.add_column(sa.Column('specimen_id', sa.Integer(), nullable=True))
        b.create_index('ix_tests_specimen_id', ['specimen_id'])
        b.create_foreign_key('fk_tests_specimen_id', 'specimens', ['specimen_id'], ['id'])


def downgrade():
    with op.batch_alter_table('tests', schema=None) as b:
        b.drop_constraint('fk_tests_specimen_id', type_='foreignkey')
        b.drop_index('ix_tests_specimen_id')
        b.drop_column('specimen_id')
