from datetime import date
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from app.database import User
from app.helpers import slugify
from .logger import Logger

logger = Logger(__name__).get_logger()

def inject_globals():
    admin = None
    try:
        user = db.session.get(User, 1)
        if user and user.is_admin:
            admin = user
    except SQLAlchemyError as e:
        logger.exception(f"Context processor DB error: {e}")

    return {
        'date': date.today(),
        'admin': admin,
        'slugify': slugify
    }