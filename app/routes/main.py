from flask import Blueprint, send_from_directory, render_template, flash, url_for, redirect, request
from app.extensions import db, sitemapper, mailer, cloudinary_client
from app.database import Post, Project, Skill, PageMeta
from app.forms import ContactForm, SkillForm, PageMetaForm
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.decorators import admin_only
from .sitemap import SITE_LASTMOD
from app.logger import Logger


logger = Logger(__name__).get_logger()

main_bp = Blueprint('main', __name__)


@sitemapper.include(lastmod=SITE_LASTMOD)
@main_bp.route("/")
def home():
    post, projects, skills = None, None, None

    try:
        post = db.session.query(Post).order_by(Post.id.desc()).first()
        projects_query = db.session.query(Project).order_by(Project.id.desc()).all()
        skills_query = db.session.query(Skill).all()

        projects = projects_query if projects_query else None
        skills = skills_query if skills_query else None

    except SQLAlchemyError as e:
        logger.exception(f"Database error on home page: {e}")
        flash("Could not load latest content.", category="danger")

    return render_template(
        'index.html',
        projects=projects,
        post=post,
        skills=skills,
        active_page='home'
    )


@sitemapper.include(lastmod=SITE_LASTMOD)
@main_bp.route("/about")
def about():
    skills = None

    try:
        skills_query = db.session.query(Skill).all()
        skills = skills_query if skills_query else None
    except SQLAlchemyError as e:
        logger.exception(f"Database error on about page: {e}")
        flash("Could not load skills list.", category="danger")

    return render_template(
        'about.html',
        active_page='about',
        skills=skills
    )


@sitemapper.include(lastmod=SITE_LASTMOD)
@main_bp.route("/contact", methods=['GET', 'POST'])
def contact():

    contact_form = ContactForm()

    if contact_form.validate_on_submit():
        response = mailer.send_email(
            email=contact_form.email.data,
            name=contact_form.name.data,
            subject=contact_form.subject.data,
            content=contact_form.message.data
        )

        if response.get("status_code", 500) >= 400:
            error_message = response.get("text", "An error occurred while sending your message.")
            flash(message=error_message, category="danger")
        else:
            flash(message="Your message has been successfully sent!", category="success")
            return redirect(url_for('main.contact'))

    return render_template(
        'contact.html',
        form=contact_form,
        active_page='contact'
    )


@main_bp.route("/add-skill", methods=["GET", "POST"])
@admin_only
def add_skill():

    form = SkillForm()

    if form.validate_on_submit():

        try:
            new_skill = Skill(
                name=form.name.data,
                icon_class=form.icon_class.data
            )
            db.session.add(new_skill)
            db.session.commit()

        except IntegrityError as e:
            db.session.rollback()
            logger.exception(f"IntegrityError: {e}")
            flash(message=f"IntegrityError: {e}", category="danger")
            return redirect(url_for('main.home'))
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.exception(f"IntegrityError: {e}")
            flash(message=f"IntegrityError: {e}", category="danger")
            return redirect(url_for('main.home'))
        else:
            flash(f"Successfully added {new_skill.name}!", "success")
            return redirect(url_for('main.home'))

    return render_template("add_skills.html", form=form)


@main_bp.route("/delete-skill/<int:skill_id>", methods=["POST"])
@admin_only
def delete_skill(skill_id):

    skill_to_delete = db.get_or_404(Skill, skill_id)

    name = skill_to_delete.name

    try:
        db.session.delete(skill_to_delete)
        db.session.commit()

    except IntegrityError as e:
        db.session.rollback()
        logger.exception(f"IntegrityError: {e}")
        flash(message=f"IntegrityError: {e}", category="danger")
        return redirect(url_for('main.home'))
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.exception(f"IntegrityError: {e}")
        flash(message=f"IntegrityError: {e}", category="danger")
        return redirect(url_for('main.home'))

    flash(f"{name} has been removed from your tech stack.", "info")
    return redirect(url_for('main.home'))


@main_bp.route("/add-meta", methods=["GET", "POST"])
@admin_only
def add_meta():

    endpoint = request.args.get('endpoint')
    existing_meta = None

    try:
        if endpoint:
            existing_meta = db.session.query(PageMeta).filter_by(endpoint=endpoint).first()
    except SQLAlchemyError as e:
        logger.exception(f"SQLAlchemyError: {e}")
        flash(message=f"SQLAlchemyError: {e}", category="danger")

    form = PageMetaForm(obj=existing_meta)

    if endpoint and request.method == "GET":
        form.endpoint.data = endpoint

    if form.validate_on_submit():

        endpoint = form.endpoint.data.strip()

        try:
            existing_meta = db.session.query(PageMeta).filter_by(endpoint=endpoint).first()
            image_url = existing_meta.image_url if existing_meta else None

            if form.image_url.data:
                image_url = form.image_url.data.strip()

            if form.image.data:
                src_url, _ = cloudinary_client.uploadImage(form.image.data, folder="MetaData", title=f"{endpoint}-meta")
                image_url = src_url

            if existing_meta:
                existing_meta.title = form.title.data.strip()
                existing_meta.description = form.description.data.strip()
                existing_meta.image_url = image_url
                existing_meta.og_type = form.og_type.data
                existing_meta.is_indexable = form.is_indexable.data
                success_message = f"Successfully updated metadata for {endpoint}!"

            else:

                new_meta = PageMeta(
                    endpoint=endpoint,
                    title=form.title.data.strip(),
                    description=form.description.data.strip(),
                    image_url=image_url,
                    og_type=form.og_type.data,
                    is_indexable=form.is_indexable.data
                )

                db.session.add(new_meta)
                success_message = f"Successfully added metadata for {endpoint}!"

            db.session.commit()

        except IntegrityError as e:
            db.session.rollback()
            logger.exception(f"IntegrityError: {e}")
            flash(message=f"IntegrityError: {e}", category="danger")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.exception(f"SQLAlchemyError: {e}")
            flash(message=f"SQLAlchemyError: {e}", category="danger")
        except Exception as e:
            db.session.rollback()
            logger.exception(f"Metadata image upload failed: {e}")
            flash(message=f"Metadata image upload failed: {e}", category="danger")
        else:
            flash(success_message, category="success")
            return redirect(url_for("main.add_meta", endpoint=endpoint))

    return render_template("add_meta.html", form=form, endpoint=endpoint, existing_meta=existing_meta)



@main_bp.route("/robots.txt")
def robots_txt():
    return send_from_directory(directory="static", path="robots.txt", mimetype="text/plain")