"""add date to day summary

Revision ID: 66a48bab1646
Revises: 1fe06d85a88d
Create Date: 2020-06-02 14:31:13.075688

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "66a48bab1646"
down_revision = "1fe06d85a88d"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("summary_day", sa.Column("date", sa.Date(), nullable=False))


def downgrade():
    op.drop_column("summary_day", "date")
