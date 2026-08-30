import os
from flask import Blueprint
from app.extensions import db, sitemapper
from app.database import Post, Project
from app.helpers import slugify, iso_today

SITE_LASTMOD = os.environ.get("SITE_LASTMOD", iso_today())

sitemap_bp = Blueprint('sitemap', __name__)

def post_sitemap_vars():
    posts = db.session.query(Post).all()
    return {
        'post_id': [post.id for post in posts],
        'slug': [slugify(post.title) for post in posts]
    }

def post_sitemap_lastmod():
    posts = db.session.query(Post).all()
    return [(post.updated_at or post.created_at).date().isoformat() for post in posts]

def project_sitemap_vars():
    projects = db.session.query(Project).all()
    return {
        'project_id': [project.id for project in projects],
        'slug': [slugify(project.title) for project in projects]
    }

def project_sitemap_lastmod():
    projects = db.session.query(Project).all()
    return [(project.updated_at or project.created_at).date().isoformat() for project in projects]


@sitemap_bp.route("/sitemap.xml")
def sitemap():
    return sitemapper.generate()