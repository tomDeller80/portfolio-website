from flask import Flask
from app.extensions import db, login_manager, bootstrap5, sitemapper, migrate, assets_env, quill, csrf
from app.helpers import slugify, format_date, cloudinary_thumb, utc_now, iso_today
from app.context_processors import inject_globals
from app.assets import compile_static_assets
from app.routes import register_blueprints
from app.hooks import redirect_to_setup
from app.routes.sitemap import sitemap
from app.database import User
from app.config import Config


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

def create_app(config_class = Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Register Blueprints
    register_blueprints(app)

    # Initialise Extensions
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap5.init_app(app)
    sitemapper.init_app(app)
    migrate.init_app(app, db)
    assets_env.init_app(app)
    quill.init_app(app)
    csrf.init_app(app)

    # Register filters
    app.add_template_filter(format_date)
    app.add_template_filter(cloudinary_thumb)

    # Context processors
    app.context_processor(inject_globals)

    # Compile static assets
    compile_static_assets(assets_env)

    # Before requests
    app.before_request(redirect_to_setup)

    return app
