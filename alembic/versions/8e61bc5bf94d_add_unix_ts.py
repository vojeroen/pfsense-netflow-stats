"""add unix ts

Revision ID: 8e61bc5bf94d
Revises: 77393fda06a9
Create Date: 2020-05-31 09:31:21.471277

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8e61bc5bf94d"
down_revision = "77393fda06a9"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "summary_minute", sa.Column("unix_end_ms", sa.BigInteger(), nullable=False)
    )
    op.add_column(
        "summary_minute", sa.Column("unix_start_ms", sa.BigInteger(), nullable=False)
    )


def downgrade():
    op.drop_column("summary_minute", "unix_start_ms")
    op.drop_column("summary_minute", "unix_end_ms")
