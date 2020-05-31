"""add processed

Revision ID: 49f6a90341dd
Revises: a745f65a9896
Create Date: 2020-05-30 06:40:06.831950

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "49f6a90341dd"
down_revision = "a745f65a9896"
branch_labels = None
depends_on = None


def add_non_nullable_col_with_value(table_name, column_name, column_type, empty_value):
    op.add_column(table_name, sa.Column(column_name, column_type))
    col = sa.table(table_name, sa.column(column_name))
    op.execute(col.update().values(**{column_name: empty_value}))
    op.alter_column(table_name, column_name, nullable=False)


def upgrade():
    add_non_nullable_col_with_value("flow", "processed", sa.Boolean(), False)


def downgrade():
    op.drop_column("flow", "processed")
