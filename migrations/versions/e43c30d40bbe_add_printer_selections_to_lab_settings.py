"""add printer selections to lab_settings

Revision ID: e43c30d40bbe
Revises: 54a03b16b0f5
Create Date: 2026-10-07 17:49:04.800582

"""
from alembic import op
import sqlalchemy as sa


revision = 'e43c30d40bbe'
down_revision = '54a03b16b0f5'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('lab_settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('printer_patient_bill', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('printer_lab_bill', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('printer_report', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('printer_barcode', sa.String(length=120), nullable=True))


def downgrade():
    with op.batch_alter_table('lab_settings', schema=None) as batch_op:
        batch_op.drop_column('printer_barcode')
        batch_op.drop_column('printer_report')
        batch_op.drop_column('printer_lab_bill')
        batch_op.drop_column('printer_patient_bill')
