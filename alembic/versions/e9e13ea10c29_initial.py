"""initial

Revision ID: e9e13ea10c29
Revises: 
Create Date: 2020-05-28 17:10:04.190585

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e9e13ea10c29"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "export_packet",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("timestamp", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "client",
        sa.Column("export_packet_id", postgresql.UUID(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("host", sa.String(), nullable=False),
        sa.Column("port", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["export_packet_id"], ["export_packet.id"],),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "flow",
        sa.Column("export_packet_id", postgresql.UUID(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("postVlanId", sa.Integer(), nullable=False),
        sa.Column("postDestinationMacAddress", sa.String(), nullable=False),
        sa.Column("sourceTransportPort", sa.Integer(), nullable=False),
        sa.Column("ipVersion", sa.Integer(), nullable=False),
        sa.Column("sourceIPv4Address", sa.String(), nullable=False),
        sa.Column("vlanId", sa.Integer(), nullable=False),
        sa.Column("octetDeltaCount", sa.Integer(), nullable=False),
        sa.Column("protocolIdentifier", sa.Integer(), nullable=False),
        sa.Column("flowStartMilliseconds", sa.BigInteger(), nullable=False),
        sa.Column("packetDeltaCount", sa.Integer(), nullable=False),
        sa.Column("tcpControlBits", sa.Integer(), nullable=False),
        sa.Column("destinationIPv4Address", sa.String(), nullable=False),
        sa.Column("egressInterface", sa.Integer(), nullable=False),
        sa.Column("sourceMacAddress", sa.String(), nullable=False),
        sa.Column("destinationTransportPort", sa.Integer(), nullable=False),
        sa.Column("ingressInterface", sa.Integer(), nullable=False),
        sa.Column("ipClassOfService", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["export_packet_id"], ["export_packet.id"],),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "header",
        sa.Column("export_packet_id", postgresql.UUID(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("length", sa.Integer(), nullable=False),
        sa.Column("export_uptime", sa.Integer(), nullable=False),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("obervation_domain_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["export_packet_id"], ["export_packet.id"],),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )


def downgrade():
    op.drop_table("header")
    op.drop_table("flow")
    op.drop_table("client")
    op.drop_table("export_packet")
