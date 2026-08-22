from functools import wraps
from flask_login import current_user
from flask import redirect, url_for, abort

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.is_admin or current_user.id != 1:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function