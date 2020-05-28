"""add system init time

Revision ID: 548ca89412b3
Revises: 0991e664f8a7
Create Date: 2020-05-28 21:21:10.241218

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "548ca89412b3"
down_revision = "0991e664f8a7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "flow", sa.Column("systemInitTimeMilliseconds", sa.BigInteger(), nullable=True)
    )
    op.alter_column(
        "flow", "destinationIPv4Address", existing_type=sa.VARCHAR(), nullable=True
    )
    op.alter_column(
        "flow", "destinationTransportPort", existing_type=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "flow", "egressInterface", existing_type=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "flow", "flowEndMilliseconds", existing_type=sa.BIGINT(), nullable=True
    )
    op.alter_column(
        "flow", "flowStartMilliseconds", existing_type=sa.BIGINT(), nullable=True
    )
    op.alter_column(
        "flow", "ingressInterface", existing_type=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "flow", "ipClassOfService", existing_type=sa.INTEGER(), nullable=True
    )
    op.alter_column("flow", "ipVersion", existing_type=sa.INTEGER(), nullable=True)
    op.alter_column(
        "flow", "octetDeltaCount", existing_type=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "flow", "packetDeltaCount", existing_type=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "flow", "postDestinationMacAddress", existing_type=sa.VARCHAR(), nullable=True
    )
    op.alter_column("flow", "postVlanId", existing_type=sa.INTEGER(), nullable=True)
    op.alter_column(
        "flow", "protocolIdentifier", existing_type=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "flow", "samplingPacketInterval", existing_type=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "flow", "samplingPacketSpace", existing_type=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "flow", "selectorAlgorithm", existing_type=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "flow", "sourceIPv4Address", existing_type=sa.VARCHAR(), nullable=True
    )
    op.alter_column(
        "flow", "sourceMacAddress", existing_type=sa.VARCHAR(), nullable=True
    )
    op.alter_column(
        "flow", "sourceTransportPort", existing_type=sa.INTEGER(), nullable=True
    )
    op.alter_column("flow", "tcpControlBits", existing_type=sa.INTEGER(), nullable=True)
    op.alter_column("flow", "vlanId", existing_type=sa.INTEGER(), nullable=True)


def downgrade():
    op.alter_column("flow", "vlanId", existing_type=sa.INTEGER(), nullable=False)
    op.alter_column(
        "flow", "tcpControlBits", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        "flow", "sourceTransportPort", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        "flow", "sourceMacAddress", existing_type=sa.VARCHAR(), nullable=False
    )
    op.alter_column(
        "flow", "sourceIPv4Address", existing_type=sa.VARCHAR(), nullable=False
    )
    op.alter_column(
        "flow", "selectorAlgorithm", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        "flow", "samplingPacketSpace", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        "flow", "samplingPacketInterval", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        "flow", "protocolIdentifier", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column("flow", "postVlanId", existing_type=sa.INTEGER(), nullable=False)
    op.alter_column(
        "flow", "postDestinationMacAddress", existing_type=sa.VARCHAR(), nullable=False
    )
    op.alter_column(
        "flow", "packetDeltaCount", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        "flow", "octetDeltaCount", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column("flow", "ipVersion", existing_type=sa.INTEGER(), nullable=False)
    op.alter_column(
        "flow", "ipClassOfService", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        "flow", "ingressInterface", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        "flow", "flowStartMilliseconds", existing_type=sa.BIGINT(), nullable=False
    )
    op.alter_column(
        "flow", "flowEndMilliseconds", existing_type=sa.BIGINT(), nullable=False
    )
    op.alter_column(
        "flow", "egressInterface", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        "flow", "destinationTransportPort", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        "flow", "destinationIPv4Address", existing_type=sa.VARCHAR(), nullable=False
    )
    op.drop_column("flow", "systemInitTimeMilliseconds")
