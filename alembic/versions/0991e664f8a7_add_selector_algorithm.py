"""add selector algorithm

Revision ID: 0991e664f8a7
Revises: 45e5433e1f63
Create Date: 2020-05-28 21:18:47.303446

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0991e664f8a7"
down_revision = "45e5433e1f63"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("flow", sa.Column("selectorAlgorithm", sa.Integer(), nullable=False))


def downgrade():
    op.drop_column("flow", "selectorAlgorithm")
