"""add metering process id

Revision ID: 0481d8d3b060
Revises: 548ca89412b3
Create Date: 2020-05-28 21:25:41.720827

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0481d8d3b060"
down_revision = "548ca89412b3"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "flow", sa.Column("meteringProcessId", sa.BigInteger(), nullable=True)
    )


def downgrade():
    op.drop_column("flow", "meteringProcessId")
