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
    op.execute("""
        UPDATE posts
        SET created_at = COALESCE(created_at, TO_TIMESTAMP(date, 'FMMonth DD, YYYY')),
            updated_at = COALESCE(updated_at, TO_TIMESTAMP(date, 'FMMonth DD, YYYY'))
        WHERE created_at IS NULL OR updated_at IS NULL
    """)

    op.execute("""
        UPDATE projects
        SET created_at = COALESCE(created_at, TO_TIMESTAMP(date, 'FMMonth DD, YYYY')),
            updated_at = COALESCE(updated_at, TO_TIMESTAMP(date, 'FMMonth DD, YYYY'))
        WHERE created_at IS NULL OR updated_at IS NULL
    """)

    op.execute("""
        UPDATE users
        SET created_at = COALESCE(created_at, NOW()),
            updated_at = COALESCE(updated_at, NOW())
        WHERE created_at IS NULL OR updated_at IS NULL
    """)

    op.execute("""
        UPDATE skills
        SET created_at = COALESCE(created_at, NOW()),
            updated_at = COALESCE(updated_at, NOW())
        WHERE created_at IS NULL OR updated_at IS NULL
    """)


def downgrade():
    pass
