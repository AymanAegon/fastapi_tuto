"""add content column to posts table

Revision ID: bd06a0e8a301
Revises: c4d4f45523e0
Create Date: 2022-03-10 21:29:07.928091

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd06a0e8a301'
down_revision = 'c4d4f45523e0'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))


def downgrade():
    op.drop_column('posts', 'content')
    pass