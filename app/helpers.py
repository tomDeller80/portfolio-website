from cloudinary import CloudinaryImage
from datetime import date, datetime, timezone
import re

def utc_now():
    return datetime.now(timezone.utc)

def iso_today():
    return date.today().isoformat()

def slugify(text):
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[\s_-]+', '-', text)

def format_date(value, fmt="%B %d, %Y"):
    if not value:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    if isinstance(value, datetime) and value.tzinfo is not None:
        value = value.astimezone(timezone.utc)
    return value.strftime(fmt)

def cloudinary_thumb(public_id, width=480):
    return CloudinaryImage(public_id).build_url(
        width=width,
        crop="limit",
        quality="auto",
        fetch_format="auto",
        secure=True
    )