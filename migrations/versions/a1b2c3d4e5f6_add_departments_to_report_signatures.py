"""add departments to report_signatures

Revision ID: a1b2c3d4e5f6
Revises: b9c8d7e6f5a4
Create Date: 2026-10-24
"""
from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "b9c8d7e6f5a4"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("report_signatures", schema=None) as batch_op:
        batch_op.add_column(sa.Column("departments", sa.JSON(), nullable=True))


def downgrade():
    with op.batch_alter_table("report_signatures", schema=None) as batch_op:
        batch_op.drop_column("departments")
