from flask import Flask
from .main import main_bp
from .auth import auth_bp
from .posts import posts_bp
from .projects import projects_bp
from .media import media_bp
from .sitemap import sitemap_bp

def register_blueprints(app: Flask) -> None:
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(media_bp)
    app.register_blueprint(sitemap_bp)