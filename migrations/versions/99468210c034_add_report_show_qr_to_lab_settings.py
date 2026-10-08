"""add report_show_qr to lab_settings

Revision ID: 99468210c034
Revises: 88dcd2f1b138
Create Date: 2026-10-08 14:09:00.213328

"""
from alembic import op
import sqlalchemy as sa


revision = '99468210c034'
down_revision = '88dcd2f1b138'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('lab_settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('report_show_qr', sa.Boolean(), nullable=False, server_default='1'))


def downgrade():
    with op.batch_alter_table('lab_settings', schema=None) as batch_op:
        batch_op.drop_column('report_show_qr')
