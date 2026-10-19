"""Add UNIQUE(rate_category_id, test_id) to rate_category_tests.

Revision ID: b9c8d7e6f5a4
Revises: f6a7b8c9d0e1
"""
from alembic import op
import sqlalchemy as sa

revision = 'b9c8d7e6f5a4'
down_revision = 'f6a7b8c9d0e1'
branch_labels = None
depends_on = None


def upgrade():
    # dedupe first
    op.execute("""
        DELETE FROM rate_category_tests
        WHERE id NOT IN (
            SELECT MIN(id) FROM rate_category_tests
            GROUP BY rate_category_id, test_id
        )
    """)
    with op.batch_alter_table('rate_category_tests', schema=None) as b:
        b.create_unique_constraint('uq_rct_cat_test', ['rate_category_id', 'test_id'])


def downgrade():
    with op.batch_alter_table('rate_category_tests', schema=None) as b:
        b.drop_constraint('uq_rct_cat_test', type_='unique')
