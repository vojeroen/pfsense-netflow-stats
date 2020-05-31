"""change data types

Revision ID: 75bc43c36299
Revises: 16e826e3e077
Create Date: 2020-05-30 08:36:54.378907

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "75bc43c36299"
down_revision = "16e826e3e077"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(None, "summary_minute", ["id"])
    op.alter_column("flow", "octetDeltaCount", type_=sa.Numeric())
    op.alter_column("flow", "packetDeltaCount", type_=sa.Numeric())
    op.alter_column("flow", "samplingPacketSpace", type_=sa.Numeric())
    op.alter_column("flow", "samplingPacketInterval", type_=sa.Numeric())
    op.alter_column("summary_minute", "connections", type_=sa.Numeric())
    op.alter_column("summary_minute", "packets", type_=sa.Numeric())
    op.alter_column("summary_minute", "octets", type_=sa.Numeric())


def downgrade():
    op.drop_constraint(None, "summary_minute", type_="unique")
    op.alter_column("flow", "octetDeltaCount", type_=sa.BigInteger())
    op.alter_column("flow", "packetDeltaCount", type_=sa.BigInteger())
    op.alter_column("flow", "samplingPacketSpace", type_=sa.Integer())
    op.alter_column("flow", "samplingPacketInterval", type_=sa.Integer())
    op.alter_column("summary_minute", "connections", type_=sa.BigInteger())
    op.alter_column("summary_minute", "packets", type_=sa.BigInteger())
    op.alter_column("summary_minute", "octets", type_=sa.BigInteger())
