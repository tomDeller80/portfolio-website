"""backfill timestamp columns

Revision ID: 457a1fc32e56
Revises: 6a921dd0c5d4
Create Date: 2026-07-18 21:27:08.033564

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '457a1fc32e56'
down_revision = '6a921dd0c5d4'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    dialect_name = bind.dialect.name

    backfill_content_timestamps('posts', inspector, dialect_name)
    backfill_content_timestamps('projects', inspector, dialect_name)
    backfill_current_timestamps('users', inspector)
    backfill_current_timestamps('skills', inspector)


def backfill_content_timestamps(table_name, inspector, dialect_name):
    if table_name not in inspector.get_table_names():
        return

    columns = {column['name'] for column in inspector.get_columns(table_name)}

    if not {'created_at', 'updated_at'}.issubset(columns):
        return

    if 'date' in columns and dialect_name == 'postgresql':
        op.execute(f"""
            UPDATE {table_name}
            SET created_at = COALESCE(created_at, TO_TIMESTAMP(date, 'FMMonth DD, YYYY')),
                updated_at = COALESCE(updated_at, TO_TIMESTAMP(date, 'FMMonth DD, YYYY'))
            WHERE created_at IS NULL OR updated_at IS NULL
        """)
        return

    backfill_current_timestamps(table_name, inspector)


def backfill_current_timestamps(table_name, inspector):
    if table_name not in inspector.get_table_names():
        return

    columns = {column['name'] for column in inspector.get_columns(table_name)}

    if not {'created_at', 'updated_at'}.issubset(columns):
        return

    op.execute(f"""
        UPDATE {table_name}
        SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP),
            updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP)
        WHERE created_at IS NULL OR updated_at IS NULL
    """)


def downgrade():
    pass
