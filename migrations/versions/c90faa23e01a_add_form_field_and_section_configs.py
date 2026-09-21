"""add form field and section configs

Revision ID: c90faa23e01a
Revises: 4f98c4fb3508
Create Date: 2026-09-16

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c90faa23e01a'
down_revision = '4f98c4fb3508'
branch_labels = None
depends_on = None


def upgrade():
    # ---------- form_field_configs ----------
    op.create_table(
        'form_field_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('field_key', sa.String(length=50), nullable=False),
        sa.Column('section', sa.String(length=30), nullable=False),
        sa.Column('is_visible', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_required', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('default_value', sa.String(length=255), nullable=True),
        sa.Column('custom_label', sa.String(length=80), nullable=True),
        sa.Column('help_text', sa.String(length=255), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('form_field_configs', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_form_field_configs_field_key'),
            ['field_key'], unique=True
        )
        batch_op.create_index(
            batch_op.f('ix_form_field_configs_section'),
            ['section'], unique=False
        )

    # ---------- form_section_configs ----------
    op.create_table(
        'form_section_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('section_key', sa.String(length=30), nullable=False),
        sa.Column('is_visible', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('form_section_configs', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_form_section_configs_section_key'),
            ['section_key'], unique=True
        )

    # ---------- lab_settings.currency_symbol ----------
    # Add with server_default so SQLite can backfill existing rows
    with op.batch_alter_table('lab_settings', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'currency_symbol',
                sa.String(length=10),
                nullable=False,
                server_default='Rs',
            )
        )


def downgrade():
    # Remove currency_symbol from lab_settings
    with op.batch_alter_table('lab_settings', schema=None) as batch_op:
        batch_op.drop_column('currency_symbol')

    # Drop form_section_configs
    with op.batch_alter_table('form_section_configs', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_form_section_configs_section_key'))
    op.drop_table('form_section_configs')

    # Drop form_field_configs
    with op.batch_alter_table('form_field_configs', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_form_field_configs_section'))
        batch_op.drop_index(batch_op.f('ix_form_field_configs_field_key'))
    op.drop_table('form_field_configs')