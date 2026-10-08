"""add report/bill/label page setup to lab_settings

Revision ID: 88dcd2f1b138
Revises: e43c30d40bbe
Create Date: 2026-10-08 11:51:59.800265

"""
from alembic import op
import sqlalchemy as sa


revision = '88dcd2f1b138'
down_revision = 'e43c30d40bbe'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('lab_settings', schema=None) as batch_op:
        # Report
        batch_op.add_column(sa.Column('report_page_size',      sa.String(length=20), nullable=False, server_default='A4'))
        batch_op.add_column(sa.Column('report_orientation',    sa.String(length=10), nullable=False, server_default='portrait'))
        batch_op.add_column(sa.Column('report_margin_top',     sa.Float(),           nullable=False, server_default='0.6'))
        batch_op.add_column(sa.Column('report_margin_bottom',  sa.Float(),           nullable=False, server_default='0.6'))
        batch_op.add_column(sa.Column('report_margin_left',    sa.Float(),           nullable=False, server_default='0.8'))
        batch_op.add_column(sa.Column('report_margin_right',   sa.Float(),           nullable=False, server_default='0.8'))
        batch_op.add_column(sa.Column('report_font_family',    sa.String(length=40), nullable=False, server_default='Helvetica'))
        batch_op.add_column(sa.Column('report_base_font_size', sa.Integer(),         nullable=False, server_default='8'))
        # Bill
        batch_op.add_column(sa.Column('bill_page_size',      sa.String(length=20), nullable=False, server_default='A4'))
        batch_op.add_column(sa.Column('bill_orientation',    sa.String(length=10), nullable=False, server_default='portrait'))
        batch_op.add_column(sa.Column('bill_margin_top',     sa.Float(),           nullable=False, server_default='0.5'))
        batch_op.add_column(sa.Column('bill_margin_bottom',  sa.Float(),           nullable=False, server_default='0.5'))
        batch_op.add_column(sa.Column('bill_margin_left',    sa.Float(),           nullable=False, server_default='0.5'))
        batch_op.add_column(sa.Column('bill_margin_right',   sa.Float(),           nullable=False, server_default='0.5'))
        batch_op.add_column(sa.Column('bill_font_family',    sa.String(length=40), nullable=False, server_default='Helvetica'))
        batch_op.add_column(sa.Column('bill_base_font_size', sa.Integer(),         nullable=False, server_default='8'))
        # Labels
        batch_op.add_column(sa.Column('label_page_size',      sa.String(length=20), nullable=False, server_default='A4'))
        batch_op.add_column(sa.Column('label_orientation',    sa.String(length=10), nullable=False, server_default='portrait'))
        batch_op.add_column(sa.Column('label_margin_top',     sa.Float(),           nullable=False, server_default='0.5'))
        batch_op.add_column(sa.Column('label_margin_bottom',  sa.Float(),           nullable=False, server_default='0.5'))
        batch_op.add_column(sa.Column('label_margin_left',    sa.Float(),           nullable=False, server_default='0.2'))
        batch_op.add_column(sa.Column('label_margin_right',   sa.Float(),           nullable=False, server_default='0.2'))
        batch_op.add_column(sa.Column('label_font_family',    sa.String(length=40), nullable=False, server_default='Helvetica'))
        batch_op.add_column(sa.Column('label_base_font_size', sa.Integer(),         nullable=False, server_default='8'))
        batch_op.add_column(sa.Column('label_grid_cols',      sa.Integer(),         nullable=False, server_default='3'))
        batch_op.add_column(sa.Column('label_grid_rows',      sa.Integer(),         nullable=False, server_default='8'))


def downgrade():
    with op.batch_alter_table('lab_settings', schema=None) as batch_op:
        for col in [
            'label_grid_rows', 'label_grid_cols', 'label_base_font_size', 'label_font_family',
            'label_margin_right', 'label_margin_left', 'label_margin_bottom', 'label_margin_top',
            'label_orientation', 'label_page_size',
            'bill_base_font_size', 'bill_font_family', 'bill_margin_right', 'bill_margin_left',
            'bill_margin_bottom', 'bill_margin_top', 'bill_orientation', 'bill_page_size',
            'report_base_font_size', 'report_font_family', 'report_margin_right', 'report_margin_left',
            'report_margin_bottom', 'report_margin_top', 'report_orientation', 'report_page_size',
        ]:
            batch_op.drop_column(col)
