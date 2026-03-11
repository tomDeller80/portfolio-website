from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from mailer import Mailer
import os

# ----- SQLAlchemy Declaration -----
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# --- Mailer Key and Declaration ---
MAILER_API_KEY = os.environ.get('MAILER_API_KEY')
MAILER_ADMIN_NAME = os.environ.get('MAILER_ADMIN_NAME')
MAILER_ADMIN_EMAIL = os.environ.get('MAILER_ADMIN_EMAIL')

mailer = Mailer(
    sender_name = MAILER_ADMIN_NAME,
    sender_email = MAILER_ADMIN_EMAIL,
    key = MAILER_API_KEY
    )