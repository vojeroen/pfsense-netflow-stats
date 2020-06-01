"""add parsed export packet

Revision ID: 89b551301248
Revises: 8e61bc5bf94d
Create Date: 2020-06-01 13:56:40.388885

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "89b551301248"
down_revision = "8e61bc5bf94d"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "parsed_export_packet",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("unix_start_ms", sa.BigInteger(), nullable=False),
        sa.Column("unix_end_ms", sa.BigInteger(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("day", sa.Integer(), nullable=False),
        sa.Column("hour", sa.Integer(), nullable=False),
        sa.Column("minute", sa.Integer(), nullable=False),
        sa.Column("offset", sa.Integer(), nullable=False),
        sa.Column("ip_version", sa.Integer(), nullable=False),
        sa.Column("protocol", sa.String(), nullable=False),
        sa.Column("local_address", sa.String(), nullable=False),
        sa.Column("local_name", sa.String(), nullable=True),
        sa.Column("remote_address", sa.String(), nullable=False),
        sa.Column("remote_name", sa.String(), nullable=True),
        sa.Column("port", sa.Integer(), nullable=False),
        sa.Column("direction", sa.String(), nullable=False),
        sa.Column("connections", sa.Numeric(), nullable=False),
        sa.Column("packets", sa.Numeric(), nullable=False),
        sa.Column("octets", sa.Numeric(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )


def downgrade():
    op.drop_table("parsed_export_packet")
