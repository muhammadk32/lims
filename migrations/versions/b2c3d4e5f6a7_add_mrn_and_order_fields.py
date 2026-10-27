"""add mrn to patients, dues_received + created_by_id to orders

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-10-27
"""
from alembic import op
import sqlalchemy as sa

revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("patients", schema=None) as batch_op:
        batch_op.add_column(sa.Column("mrn", sa.String(50), nullable=True))
        batch_op.create_index("ix_patients_mrn", ["mrn"], unique=False)

    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.add_column(sa.Column("dues_received", sa.Float(), nullable=False, server_default="0.0"))
        batch_op.add_column(sa.Column("created_by_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_orders_created_by_id", ["created_by_id"], unique=False)
        batch_op.create_foreign_key("fk_orders_created_by_id_users", "users", ["created_by_id"], ["id"])


def downgrade():
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.drop_constraint("fk_orders_created_by_id_users", type_="foreignkey")
        batch_op.drop_index("ix_orders_created_by_id")
        batch_op.drop_column("created_by_id")
        batch_op.drop_column("dues_received")

    with op.batch_alter_table("patients", schema=None) as batch_op:
        batch_op.drop_index("ix_patients_mrn")
        batch_op.drop_column("mrn")
