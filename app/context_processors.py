from sqlalchemy.exc import SQLAlchemyError
from app.helpers import slugify
from app.extensions import db
from app.database import User,PageMeta
from datetime import date
from .logger import Logger
from flask import request

logger = Logger(__name__).get_logger()

def inject_globals():
    admin, page_meta = None, None
    try:

        user = db.session.get(User, 1)
        if user and user.is_admin:
            admin = user

        if request.endpoint:
            page_meta = db.session.query(PageMeta
            ).filter_by(endpoint=request.endpoint).first()

    except SQLAlchemyError as e:
        logger.exception(f"Context processor DB error: {e}")

    return {
        'date': date.today(),
        'admin': admin,
        'slugify': slugify,
        'page_meta': page_meta
    }