"""add icmp type code

Revision ID: a745f65a9896
Revises: d535c27dfcd7
Create Date: 2020-05-28 21:49:47.467536

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a745f65a9896"
down_revision = "d535c27dfcd7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("flow", sa.Column("icmpTypeCodeIPv4", sa.Integer(), nullable=True))
    op.add_column("flow", sa.Column("icmpTypeCodeIPv6", sa.Integer(), nullable=True))


def downgrade():
    op.drop_column("flow", "icmpTypeCodeIPv6")
    op.drop_column("flow", "icmpTypeCodeIPv4")
