"""add layout_html to pcr_templates"""
from alembic import op
import sqlalchemy as sa

revision = 'f2cca433fe94'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('pcr_templates', schema=None) as batch_op:
        batch_op.add_column(sa.Column('layout_html', sa.Text(), nullable=True))

def downgrade():
    with op.batch_alter_table('pcr_templates', schema=None) as batch_op:
        batch_op.drop_column('layout_html')
