from flask import request, redirect, url_for
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from app.database import User
from app.logger import Logger

logger = Logger(__name__).get_logger()

def redirect_to_setup():

    allowed_endpoints = ['auth.setup', 'auth.login', 'auth.logout', 'main.robots_txt', 'static',]
    if request.endpoint in allowed_endpoints or not request.endpoint:
        return

    if request.path == url_for('auth.setup') and request.method == 'POST':
        return

    try:

        inspector = inspect(db.engine)

        if not inspector.has_table(User.__tablename__):
            logger.warning("No users table found in database. Redirecting to setup.")
            return redirect(url_for('auth.setup'))

        admin_exists = db.session.query(User).filter(User.is_admin.is_(True)).first()

        if not admin_exists:
            logger.warning("No admin found in database. Redirecting to setup.")
            return redirect(url_for('auth.setup'))

    except SQLAlchemyError as e:
        logger.error(f"Database check failed: {e}")
        return redirect(url_for('auth.setup'))