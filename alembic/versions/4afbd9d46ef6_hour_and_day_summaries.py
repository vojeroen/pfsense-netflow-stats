"""hour and day summaries

Revision ID: 4afbd9d46ef6
Revises: 10866f584d19
Create Date: 2020-06-02 13:19:37.865338

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "4afbd9d46ef6"
down_revision = "10866f584d19"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "summary_day",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("unix_start_ms", sa.BigInteger(), nullable=False),
        sa.Column("unix_end_ms", sa.BigInteger(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("day", sa.Integer(), nullable=False),
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
    op.create_table(
        "summary_hour",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("unix_start_ms", sa.BigInteger(), nullable=False),
        sa.Column("unix_end_ms", sa.BigInteger(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("day", sa.Integer(), nullable=False),
        sa.Column("hour", sa.Integer(), nullable=False),
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
    op.create_unique_constraint(None, "summary_update_time", ["id"])


def downgrade():
    op.drop_constraint(None, "summary_update_time", type_="unique")
    op.drop_table("summary_hour")
    op.drop_table("summary_day")
