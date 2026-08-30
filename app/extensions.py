import os
from app.services import MailerService, CloudinaryService
from flask_assets import Environment, Bundle
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_sitemapper import Sitemapper
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_quill import Quill
import cloudinary

db = SQLAlchemy()
login_manager = LoginManager()
bootstrap5 = Bootstrap5()
sitemapper = Sitemapper()
assets_env = Environment()
csrf = CSRFProtect()
migrate = Migrate()
quill = Quill()

# Mailer instance
mailer = MailerService(
    sender_name=os.environ.get('MAILER_ADMIN_NAME'),
    sender_email=os.environ.get('MAILER_ADMIN_EMAIL'),
    key=os.environ.get('MAILER_API_KEY')
)

# Cloudinary global config
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_KEY'),
    api_secret=os.environ.get('CLOUDINARY_SECRET'),
    secure=True
)

cloudinary_client = CloudinaryService()

