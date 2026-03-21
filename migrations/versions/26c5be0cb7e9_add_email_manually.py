"""add email manually

Revision ID: 26c5be0cb7e9
Revises: 
Create Date: 2026-03-21 13:27:43.639027

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '26c5be0cb7e9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('inquiry', sa.Column('email', sa.String(length=120), nullable=True))


def downgrade():
    op.drop_column('inquiry', 'email')