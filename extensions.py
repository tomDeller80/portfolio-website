from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from mailer import Mailer
import os

# ----- SQLAlchemy Declaration -----
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


# --- Mailer Key and Declaration ---
MAILER_API_KEY = (
     os.environ.get('MAILER_API_KEY')
)

mailer = Mailer(
    sender_name = 'Thomas',
    sender_email = 'tom@deller.co',
    key = MAILER_API_KEY
    )


