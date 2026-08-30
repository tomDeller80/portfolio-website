"""initial schema

Revision ID: 6a921dd0c5d4
Revises: 
Create Date: 2026-07-18 20:20:41.550672

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a921dd0c5d4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if 'users' not in tables:
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=250), nullable=False),
            sa.Column('email', sa.String(length=250), nullable=False),
            sa.Column('password', sa.String(length=250), nullable=False),
            sa.Column('job_title', sa.String(length=250), nullable=True),
            sa.Column('pronoun', sa.String(length=250), nullable=False),
            sa.Column('tagline', sa.String(length=500), nullable=True),
            sa.Column('about', sa.Text(), nullable=False),
            sa.Column('location', sa.String(length=250), nullable=True),
            sa.Column('linkedin', sa.String(length=500), nullable=False),
            sa.Column('github', sa.String(length=500), nullable=False),
            sa.Column('profile_img', sa.String(length=500), nullable=True),
            sa.Column('resume_url', sa.String(length=500), nullable=True),
            sa.Column('is_admin', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('email'),
            sa.UniqueConstraint('name')
        )
    else:
        add_timestamp_columns('users', inspector)

    if 'skills' not in tables:
        op.create_table(
            'skills',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=250), nullable=False),
            sa.Column('icon_class', sa.String(length=250), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )
    else:
        add_timestamp_columns('skills', inspector)

    if 'posts' not in tables:
        op.create_table(
            'posts',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=250), nullable=False),
            sa.Column('subtitle', sa.String(length=250), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('body', sa.Text(), nullable=False),
            sa.Column('img_url', sa.String(length=250), nullable=False),
            sa.Column('tags', sa.Text(), nullable=False),
            sa.Column('author_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['author_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('title')
        )
    else:
        add_timestamp_columns('posts', inspector)

    if 'projects' not in tables:
        op.create_table(
            'projects',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=250), nullable=False),
            sa.Column('subtitle', sa.String(length=250), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('body', sa.Text(), nullable=False),
            sa.Column('img_url', sa.String(length=250), nullable=False),
            sa.Column('github_url', sa.String(length=500), nullable=True),
            sa.Column('demo_url', sa.String(length=500), nullable=False),
            sa.Column('tags', sa.Text(), nullable=False),
            sa.Column('author_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['author_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('title')
        )
    else:
        add_timestamp_columns('projects', inspector)

    if 'galleries' not in tables:
        op.create_table(
            'galleries',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('post_id', sa.Integer(), nullable=True),
            sa.Column('project_id', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['post_id'], ['posts.id']),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
            sa.PrimaryKeyConstraint('id')
        )

    if 'gallery_images' not in tables:
        op.create_table(
            'gallery_images',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('public_id', sa.String(length=500), nullable=False),
            sa.Column('title', sa.String(length=250), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('tags', sa.Text(), nullable=True),
            sa.Column('alt_text', sa.String(length=250), nullable=False),
            sa.Column('gallery_id', sa.Integer(), nullable=False),
            sa.Column('url', sa.String(length=500), nullable=False),
            sa.Column('position', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['gallery_id'], ['galleries.id']),
            sa.PrimaryKeyConstraint('id')
        )


def add_timestamp_columns(table_name, inspector):
    columns = {column['name'] for column in inspector.get_columns(table_name)}

    with op.batch_alter_table(table_name, schema=None) as batch_op:
        if 'created_at' not in columns:
            batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))
        if 'updated_at' not in columns:
            batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')

    with op.batch_alter_table('skills', schema=None) as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')

    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')

    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###
