"""add ipv6

Revision ID: d535c27dfcd7
Revises: 0481d8d3b060
Create Date: 2020-05-28 21:41:51.936427

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d535c27dfcd7"
down_revision = "0481d8d3b060"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "flow", sa.Column("destinationIPv6Address", sa.String(), nullable=True)
    )
    op.add_column(
        "flow", sa.Column("destinationMacAddress", sa.String(), nullable=True)
    )
    op.add_column("flow", sa.Column("sourceIPv6Address", sa.String(), nullable=True))


def downgrade():
    op.drop_column("flow", "sourceIPv6Address")
    op.drop_column("flow", "destinationMacAddress")
    op.drop_column("flow", "destinationIPv6Address")
