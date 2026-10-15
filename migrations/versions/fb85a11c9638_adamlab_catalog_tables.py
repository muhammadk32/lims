"""adamlab catalog tables

Revision ID: fb85a11c9638
Revises: 63cdd83c55b4
Create Date: 2026-10-15 12:29:33.704818
"""
from alembic import op
import sqlalchemy as sa


revision = 'fb85a11c9638'
down_revision = '63cdd83c55b4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('antimicrobial_groups',
        sa.Column('code', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('antimicrobial_groups') as b:
        b.create_index('ix_antimicrobial_groups_code', ['code'], unique=True)

    op.create_table('antimicrobials',
        sa.Column('adamlab_id', sa.Integer(), nullable=True),
        sa.Column('code', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('short_name', sa.String(length=10), nullable=True),
        sa.Column('shortcut_name', sa.String(length=15), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('antimicrobials') as b:
        b.create_index('ix_antimicrobials_adamlab_id', ['adamlab_id'], unique=True)
        b.create_index('ix_antimicrobials_code', ['code'], unique=False)

    op.create_table('culture_bacteria',
        sa.Column('adamlab_code', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('culture_bacteria') as b:
        b.create_index('ix_culture_bacteria_adamlab_code', ['adamlab_code'], unique=True)

    op.create_table('culture_medicines',
        sa.Column('adamlab_code', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=120), nullable=True),
        sa.Column('short_name', sa.String(length=40), nullable=True),
        sa.Column('resistant', sa.Integer(), nullable=True),
        sa.Column('lab_code', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('culture_medicines') as b:
        b.create_index('ix_culture_medicines_adamlab_code', ['adamlab_code'], unique=True)

    op.create_table('lab_departments',
        sa.Column('code', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('lab_departments') as b:
        b.create_index('ix_lab_departments_code', ['code'], unique=True)

    op.create_table('rate_categories',
        sa.Column('code', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('rate_categories') as b:
        b.create_index('ix_rate_categories_code', ['code'], unique=True)

    op.create_table('specimen_categories',
        sa.Column('code', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('specimen_categories') as b:
        b.create_index('ix_specimen_categories_code', ['code'], unique=True)

    op.create_table('sub_departments',
        sa.Column('code', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('sub_departments') as b:
        b.create_index('ix_sub_departments_code', ['code'], unique=True)

    op.create_table('test_cutoffs',
        sa.Column('test_code', sa.String(length=60), nullable=True),
        sa.Column('parameter', sa.String(length=120), nullable=False),
        sa.Column('cutoff_value', sa.String(length=80), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('test_cutoffs') as b:
        b.create_index('ix_test_cutoffs_test_code', ['test_code'], unique=False)

    op.create_table('test_days',
        sa.Column('adamlab_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.String(length=120), nullable=False),
        sa.Column('report_date', sa.String(length=60), nullable=True),
        sa.Column('report_time', sa.Integer(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('test_days') as b:
        b.create_index('ix_test_days_adamlab_id', ['adamlab_id'], unique=True)

    op.create_table('lab_sections',
        sa.Column('code', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['department_id'], ['lab_departments.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('lab_sections') as b:
        b.create_index('ix_lab_sections_code', ['code'], unique=True)

    op.create_table('rate_category_rates',
        sa.Column('rate_category_id', sa.Integer(), nullable=False),
        sa.Column('company_code', sa.Integer(), nullable=True),
        sa.Column('section_code', sa.Integer(), nullable=True),
        sa.Column('rate_percent', sa.Numeric(precision=18, scale=0), nullable=True),
        sa.Column('commission', sa.Numeric(precision=8, scale=0), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['rate_category_id'], ['rate_categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('rate_category_rates') as b:
        b.create_index('ix_rate_category_rates_company_code', ['company_code'], unique=False)
        b.create_index('ix_rate_category_rates_rate_category_id', ['rate_category_id'], unique=False)
        b.create_index('ix_rate_category_rates_section_code', ['section_code'], unique=False)

    op.create_table('specimens',
        sa.Column('code', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['specimen_categories.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('specimens') as b:
        b.create_index('ix_specimens_code', ['code'], unique=True)

    op.create_table('rate_category_tests',
        sa.Column('rate_category_id', sa.Integer(), nullable=False),
        sa.Column('test_id', sa.Integer(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['rate_category_id'], ['rate_categories.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['test_id'], ['tests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('rate_category_tests') as b:
        b.create_index('ix_rate_category_tests_rate_category_id', ['rate_category_id'], unique=False)
        b.create_index('ix_rate_category_tests_test_id', ['test_id'], unique=False)

    op.create_table('sub_department_tests',
        sa.Column('sub_department_id', sa.Integer(), nullable=False),
        sa.Column('test_id', sa.Integer(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['sub_department_id'], ['sub_departments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['test_id'], ['tests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('sub_department_tests') as b:
        b.create_index('ix_sub_department_tests_sub_department_id', ['sub_department_id'], unique=False)
        b.create_index('ix_sub_department_tests_test_id', ['test_id'], unique=False)

    op.create_table('test_default_results',
        sa.Column('adamlab_resultcode', sa.Integer(), nullable=True),
        sa.Column('test_id', sa.Integer(), nullable=False),
        sa.Column('result_name', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['test_id'], ['tests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('test_default_results') as b:
        b.create_index('ix_test_default_results_adamlab_resultcode', ['adamlab_resultcode'], unique=True)
        b.create_index('ix_test_default_results_test_id', ['test_id'], unique=False)

    op.create_table('test_parameters',
        sa.Column('adamlab_id', sa.Integer(), nullable=True),
        sa.Column('test_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('report_name', sa.String(length=120), nullable=True),
        sa.Column('unit', sa.String(length=60), nullable=True),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('is_editable', sa.Boolean(), nullable=False),
        sa.Column('format', sa.String(length=20), nullable=True),
        sa.Column('parameter_name', sa.String(length=60), nullable=True),
        sa.Column('parameter_code', sa.Integer(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('is_calculated', sa.Boolean(), nullable=False),
        sa.Column('formula', sa.String(length=500), nullable=True),
        sa.Column('critical_low', sa.Float(), nullable=True),
        sa.Column('critical_high', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['test_id'], ['tests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('test_parameters') as b:
        b.create_index('ix_test_parameters_adamlab_id', ['adamlab_id'], unique=True)
        b.create_index('ix_test_parameters_test_id', ['test_id'], unique=False)

    op.create_table('test_remark_templates',
        sa.Column('adamlab_recordid', sa.Integer(), nullable=True),
        sa.Column('test_id', sa.Integer(), nullable=False),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('fixed_remarks', sa.Text(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['test_id'], ['tests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('test_remark_templates') as b:
        b.create_index('ix_test_remark_templates_adamlab_recordid', ['adamlab_recordid'], unique=True)
        b.create_index('ix_test_remark_templates_test_id', ['test_id'], unique=False)

    op.create_table('test_parameter_normal_values',
        sa.Column('adamlab_id', sa.Integer(), nullable=True),
        sa.Column('parameter_id', sa.Integer(), nullable=False),
        sa.Column('gender', sa.Integer(), nullable=False),
        sa.Column('age_min', sa.Integer(), nullable=True),
        sa.Column('age_max', sa.Integer(), nullable=True),
        sa.Column('age_type', sa.String(length=20), nullable=True),
        sa.Column('value_from', sa.Float(), nullable=True),
        sa.Column('value_to', sa.Float(), nullable=True),
        sa.Column('text_value', sa.Text(), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['parameter_id'], ['test_parameters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('test_parameter_normal_values') as b:
        b.create_index('ix_test_parameter_normal_values_adamlab_id', ['adamlab_id'], unique=True)
        b.create_index('ix_test_parameter_normal_values_parameter_id', ['parameter_id'], unique=False)

    with op.batch_alter_table('tests') as b:
        b.add_column(sa.Column('adamlab_id', sa.Integer(), nullable=True))
        b.create_index('ix_tests_adamlab_id', ['adamlab_id'], unique=True)
        b.create_index('ix_tests_is_outsourced', ['is_outsourced'], unique=False)
        b.create_index('ix_tests_is_panel', ['is_panel'], unique=False)
        b.create_index('ix_tests_result_format', ['result_format'], unique=False)


def downgrade():
    with op.batch_alter_table('tests') as b:
        b.drop_index('ix_tests_result_format')
        b.drop_index('ix_tests_is_panel')
        b.drop_index('ix_tests_is_outsourced')
        b.drop_index('ix_tests_adamlab_id')
        b.drop_column('adamlab_id')

    op.drop_table('test_parameter_normal_values')
    op.drop_table('test_remark_templates')
    op.drop_table('test_parameters')
    op.drop_table('test_default_results')
    op.drop_table('sub_department_tests')
    op.drop_table('rate_category_tests')
    op.drop_table('specimens')
    op.drop_table('rate_category_rates')
    op.drop_table('lab_sections')
    op.drop_table('test_days')
    op.drop_table('test_cutoffs')
    op.drop_table('sub_departments')
    op.drop_table('specimen_categories')
    op.drop_table('rate_categories')
    op.drop_table('lab_departments')
    op.drop_table('culture_medicines')
    op.drop_table('culture_bacteria')
    op.drop_table('antimicrobials')
    op.drop_table('antimicrobial_groups')