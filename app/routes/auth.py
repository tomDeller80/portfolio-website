from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, request, url_for, redirect, flash, render_template
from flask_login import login_user, logout_user, current_user, login_required
from wtforms.validators import Optional, Length, EqualTo
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.forms import SetupForm, LoginForm
from app.decorators import admin_only
from sqlalchemy import inspect
from app.database import User
from app.logger import Logger
from app.extensions import db, cloudinary_client

logger = Logger(__name__).get_logger()
auth_bp = Blueprint('auth', __name__)


def upload_profile_image(form):
    profile_img = form.profile_img.data.strip() if form.profile_img.data else None

    if form.profile_image_upload.data:
        try:
            src_url, _ = cloudinary_client.uploadImage(
                form.profile_image_upload.data,
                folder="Profile",
                title=f"{form.name.data}-profile"
            )
            profile_img = src_url
        except Exception as e:
            logger.exception(f"Error uploading profile image: {e}")
            flash(f"Error uploading profile image: {e}", "danger")

    return profile_img


@auth_bp.route('/setup', methods=['GET', 'POST'])
def setup():

    try:

        inspector = inspect(db.engine)

        if not inspector.has_table(User.__tablename__):
            db.create_all()

        existing_admin = db.session.query(User).filter_by(id=1, is_admin=True).first()

        if existing_admin:
            flash( message="Setup already completed. Please log in.", category="info")
            return redirect(url_for('auth.login'))

    except IntegrityError as e:
        logger.exception(f"IntegrityError: {e}")
        flash(message=f"IntegrityError: {e}", category="danger")

    except SQLAlchemyError as e:
        logger.exception(f"SQLAlchemyError: {e}")
        flash(message=f"SQLAlchemyError: {e}", category="danger")

    form = SetupForm()

    if form.validate_on_submit():

        hashed_pw = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )

        try:

            profile_img = upload_profile_image(form)

            new_admin = User(
                name=form.name.data,
                email=form.email.data,
                password=hashed_pw,
                job_title=form.job_title.data,
                pronoun=form.pronoun.data,
                tagline=form.tagline.data,
                about=form.about.data,
                location=form.location.data,
                profile_img=profile_img,
                resume_url = form.resume_url.data,
                linkedin=form.linkedin.data,
                github=form.github.data,
                is_admin = True
            )

            db.session.add(new_admin)
            db.session.commit()

            flash("Admin account created successfully! You can now log in.", "success")
            return redirect(url_for('auth.login'))

        except IntegrityError as e:
            db.session.rollback()
            logger.exception(f"IntegrityError: {e}")
            flash(message=f"IntegrityError: {e}", category="danger")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.exception(f"SQLAlchemyError: {e}")
            flash(message=f"SQLAlchemyError: {e}", category="danger")

    elif request.method == 'POST':
        logger.error(f"Form Validation Failed! Errors: {form.errors}")


    return render_template(template_name_or_list="setup.html", form=form, admin=None)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        flash(message='You are already signed in.', category='success')
        return redirect(url_for('main.home'))

    form = LoginForm()

    if form.validate_on_submit():

        try:
            user = db.session.query(User).filter_by(email=form.email.data).first()
        except SQLAlchemyError as e:
            logger.exception(f"SQLAlchemyError: {e}")
            flash(message=f"Failed to access credentials!", category="danger")
        else:

            if user and check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                flash(message='You have been successfully logged in.', category='success')
                return redirect(url_for('main.home'))
            else:
                flash(message='Invalid email or password.', category='danger')

    return render_template(template_name_or_list='login.html', form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash(message='You have been successfully logged out.', category='success')
    return redirect(url_for('main.home'))


@auth_bp.route("/edit-profile", methods=["GET", "POST"])
@admin_only
def edit_profile():

    admin_user = current_user

    form = SetupForm(obj=admin_user)

    if admin_user:
        form.password.validators = [Optional(strip_whitespace=True), Length(min=8)]
        form.confirm_password.validators = [Optional(strip_whitespace=True),
                                            EqualTo('password', message="Passwords must match.")]

    if form.validate_on_submit():

        try:

            admin_user.name = form.name.data
            admin_user.email = form.email.data

            if form.password.data and form.password.data.strip():
                admin_user.password = generate_password_hash(
                    form.password.data.strip(),
                    method='pbkdf2:sha256',
                    salt_length=8
                )

            admin_user.job_title = form.job_title.data
            admin_user.pronoun = form.pronoun.data
            admin_user.tagline = form.tagline.data
            admin_user.about = form.about.data
            admin_user.location = form.location.data
            admin_user.profile_img = upload_profile_image(form)
            admin_user.resume_url = form.resume_url.data
            admin_user.linkedin = form.linkedin.data
            admin_user.github = form.github.data

            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for('main.home'))

        except IntegrityError as e:
            db.session.rollback()
            logger.exception(f"IntegrityError: {e}")
            flash("An account with that email already exists.", category="danger")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.exception(f"SQLAlchemyError: {e}")
            flash("Database error updating profile.", category="danger")

    elif request.method == 'POST':
        logger.error(f"Edit profile validation failed: {form.errors}")


    return render_template("setup.html", form=form, admin=admin_user)
