"""remove tables for raw export packets

Revision ID: edc5d2a45137
Revises: f43c022271a8
Create Date: 2020-06-01 21:03:31.641708

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "edc5d2a45137"
down_revision = "f43c022271a8"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("header")
    op.drop_table("client")
    op.drop_table("flow")
    op.drop_table("export_packet")


def downgrade():
    op.create_table(
        "export_packet",
        sa.Column("id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column("timestamp", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("id", name="export_packet_pkey"),
        sa.UniqueConstraint("id", name="export_packet_id_key"),
        postgresql_ignore_search_path=False,
    )
    op.create_table(
        "flow",
        sa.Column(
            "export_packet_id", postgresql.UUID(), autoincrement=False, nullable=True
        ),
        sa.Column("id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column("postVlanId", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column(
            "postDestinationMacAddress",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "sourceTransportPort", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.Column("ipVersion", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column(
            "sourceIPv4Address", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
        sa.Column("vlanId", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("octetDeltaCount", sa.NUMERIC(), autoincrement=False, nullable=True),
        sa.Column(
            "protocolIdentifier", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "flowStartMilliseconds", sa.BIGINT(), autoincrement=False, nullable=True
        ),
        sa.Column("packetDeltaCount", sa.NUMERIC(), autoincrement=False, nullable=True),
        sa.Column("tcpControlBits", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column(
            "destinationIPv4Address", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
        sa.Column("egressInterface", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("sourceMacAddress", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "destinationTransportPort", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.Column("ingressInterface", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("ipClassOfService", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column(
            "flowEndMilliseconds", sa.BIGINT(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "samplingPacketInterval", sa.NUMERIC(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "samplingPacketSpace", sa.NUMERIC(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "selectorAlgorithm", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "systemInitTimeMilliseconds",
            sa.BIGINT(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("meteringProcessId", sa.BIGINT(), autoincrement=False, nullable=True),
        sa.Column(
            "destinationIPv6Address", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "destinationMacAddress", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "sourceIPv6Address", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
        sa.Column("icmpTypeCodeIPv4", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("icmpTypeCodeIPv6", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("processed", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["export_packet_id"],
            ["export_packet.id"],
            name="flow_export_packet_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="flow_pkey"),
        sa.UniqueConstraint("id", name="flow_id_key"),
    )
    op.create_table(
        "client",
        sa.Column(
            "export_packet_id", postgresql.UUID(), autoincrement=False, nullable=True
        ),
        sa.Column("id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column("host", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("port", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["export_packet_id"],
            ["export_packet.id"],
            name="client_export_packet_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="client_pkey"),
        sa.UniqueConstraint("id", name="client_id_key"),
    )
    op.create_table(
        "header",
        sa.Column(
            "export_packet_id", postgresql.UUID(), autoincrement=False, nullable=True
        ),
        sa.Column("id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column("version", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("length", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("export_uptime", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("sequence_number", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "obervation_domain_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["export_packet_id"],
            ["export_packet.id"],
            name="header_export_packet_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="header_pkey"),
        sa.UniqueConstraint("id", name="header_id_key"),
    )
