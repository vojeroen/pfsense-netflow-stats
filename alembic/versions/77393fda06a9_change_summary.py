"""change summary

Revision ID: 77393fda06a9
Revises: 75bc43c36299
Create Date: 2020-05-31 09:07:59.369509

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "77393fda06a9"
down_revision = "75bc43c36299"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("summary_minute", sa.Column("direction", sa.String(), nullable=False))
    op.add_column(
        "summary_minute", sa.Column("local_address", sa.String(), nullable=False)
    )
    op.add_column("summary_minute", sa.Column("local_name", sa.String(), nullable=True))
    op.add_column("summary_minute", sa.Column("port", sa.Integer(), nullable=False))
    op.add_column(
        "summary_minute", sa.Column("remote_address", sa.String(), nullable=False)
    )
    op.add_column(
        "summary_minute", sa.Column("remote_name", sa.String(), nullable=True)
    )
    op.drop_column("summary_minute", "destination_port")
    op.drop_column("summary_minute", "source_port")
    op.drop_column("summary_minute", "destination_ipv6_address")
    op.drop_column("summary_minute", "destination_mac_address")
    op.drop_column("summary_minute", "source_mac_address")
    op.drop_column("summary_minute", "source_ipv6_address")
    op.drop_column("summary_minute", "destination_ipv4_address")
    op.drop_column("summary_minute", "source_ipv4_address")


def downgrade():
    op.add_column(
        "summary_minute",
        sa.Column(
            "source_ipv4_address", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "summary_minute",
        sa.Column(
            "destination_ipv4_address", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "summary_minute",
        sa.Column(
            "source_ipv6_address", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "summary_minute",
        sa.Column(
            "source_mac_address", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
    )
    op.add_column(
        "summary_minute",
        sa.Column(
            "destination_mac_address", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
    )
    op.add_column(
        "summary_minute",
        sa.Column(
            "destination_ipv6_address", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "summary_minute",
        sa.Column("source_port", sa.INTEGER(), autoincrement=False, nullable=False),
    )
    op.add_column(
        "summary_minute",
        sa.Column(
            "destination_port", sa.INTEGER(), autoincrement=False, nullable=False
        ),
    )
    op.drop_column("summary_minute", "remote_name")
    op.drop_column("summary_minute", "remote_address")
    op.drop_column("summary_minute", "port")
    op.drop_column("summary_minute", "local_name")
    op.drop_column("summary_minute", "local_address")
    op.drop_column("summary_minute", "direction")
