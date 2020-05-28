"""add sampling packet

Revision ID: 45e5433e1f63
Revises: e9e13ea10c29
Create Date: 2020-05-28 17:50:21.412925

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "45e5433e1f63"
down_revision = "e9e13ea10c29"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(None, "client", ["id"])
    op.create_unique_constraint(None, "export_packet", ["id"])
    op.add_column(
        "flow", sa.Column("flowEndMilliseconds", sa.BigInteger(), nullable=False)
    )
    op.add_column(
        "flow", sa.Column("samplingPacketInterval", sa.Integer(), nullable=False)
    )
    op.add_column(
        "flow", sa.Column("samplingPacketSpace", sa.Integer(), nullable=False)
    )
    op.create_unique_constraint(None, "flow", ["id"])
    op.create_unique_constraint(None, "header", ["id"])


def downgrade():
    op.drop_constraint(None, "header", type_="unique")
    op.drop_constraint(None, "flow", type_="unique")
    op.drop_column("flow", "samplingPacketSpace")
    op.drop_column("flow", "samplingPacketInterval")
    op.drop_column("flow", "flowEndMilliseconds")
    op.drop_constraint(None, "export_packet", type_="unique")
    op.drop_constraint(None, "client", type_="unique")
