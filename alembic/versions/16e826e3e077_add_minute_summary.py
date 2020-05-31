"""add minute summary

Revision ID: 16e826e3e077
Revises: 49f6a90341dd
Create Date: 2020-05-30 07:00:21.362601

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "16e826e3e077"
down_revision = "49f6a90341dd"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "summary_minute",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("day", sa.Integer(), nullable=False),
        sa.Column("hour", sa.Integer(), nullable=False),
        sa.Column("minute", sa.Integer(), nullable=False),
        sa.Column("offset", sa.Integer(), nullable=False),
        sa.Column("ip_version", sa.Integer(), nullable=False),
        sa.Column("protocol", sa.String(), nullable=False),
        sa.Column("source_mac_address", sa.String(), nullable=False),
        sa.Column("source_ipv4_address", sa.String(), nullable=True),
        sa.Column("source_ipv6_address", sa.String(), nullable=True),
        sa.Column("source_port", sa.Integer(), nullable=False),
        sa.Column("destination_mac_address", sa.String(), nullable=False),
        sa.Column("destination_ipv4_address", sa.String(), nullable=True),
        sa.Column("destination_ipv6_address", sa.String(), nullable=True),
        sa.Column("destination_port", sa.Integer(), nullable=False),
        sa.Column("connections", sa.Integer(), nullable=False),
        sa.Column("packets", sa.BigInteger(), nullable=False),
        sa.Column("octets", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )


def downgrade():
    op.drop_table("summary_minute")
