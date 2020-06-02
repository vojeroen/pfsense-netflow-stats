"""remove unix ts from day summary

Revision ID: 1fe06d85a88d
Revises: 4afbd9d46ef6
Create Date: 2020-06-02 13:36:02.352733

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1fe06d85a88d"
down_revision = "4afbd9d46ef6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(None, "summary_day", ["id"])
    op.drop_column("summary_day", "unix_end_ms")
    op.drop_column("summary_day", "unix_start_ms")
    op.create_unique_constraint(None, "summary_hour", ["id"])


def downgrade():
    op.drop_constraint(None, "summary_hour", type_="unique")
    op.add_column(
        "summary_day",
        sa.Column("unix_start_ms", sa.BIGINT(), autoincrement=False, nullable=False),
    )
    op.add_column(
        "summary_day",
        sa.Column("unix_end_ms", sa.BIGINT(), autoincrement=False, nullable=False),
    )
    op.drop_constraint(None, "summary_day", type_="unique")
