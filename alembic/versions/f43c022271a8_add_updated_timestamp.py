"""add updated timestamp

Revision ID: f43c022271a8
Revises: 89b551301248
Create Date: 2020-06-01 14:20:40.115394

"""
import datetime

import pytz
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f43c022271a8"
down_revision = "89b551301248"
branch_labels = None
depends_on = None


def ts_to_ms(ts):
    return int(
        (ts - pytz.utc.localize(datetime.datetime(1970, 1, 1))).total_seconds() * 1000
    )


def add_non_nullable_col_with_value(table_name, column_name, column_type, empty_value):
    op.add_column(table_name, sa.Column(column_name, column_type))
    col = sa.table(table_name, sa.column(column_name))
    op.execute(col.update().values(**{column_name: empty_value}))
    op.alter_column(table_name, column_name, nullable=False)


def upgrade():
    add_non_nullable_col_with_value(
        "parsed_export_packet",
        "unix_updated_ms",
        sa.BigInteger(),
        ts_to_ms(pytz.utc.localize(datetime.datetime.utcnow())),
    )
    op.create_unique_constraint(None, "parsed_export_packet", ["id"])


def downgrade():
    op.drop_constraint(None, "parsed_export_packet", type_="unique")
    op.drop_column("parsed_export_packet", "unix_updated_ms")
