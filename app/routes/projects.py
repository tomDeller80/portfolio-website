from flask import Blueprint, render_template, flash, url_for, redirect, abort
from .sitemap import project_sitemap_vars, project_sitemap_lastmod, SITE_LASTMOD
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.extensions import sitemapper, db, cloudinary_client
from flask_login import current_user
from app.forms import CreateProjectForm
from app.decorators import admin_only
from app.helpers import slugify
from app.database import Project
from app.logger import Logger

logger = Logger(__name__).get_logger()

projects_bp = Blueprint('projects', __name__)


@sitemapper.include(url_variables=project_sitemap_vars, lastmod=project_sitemap_lastmod)
@projects_bp.route("/project/<int:project_id>")
@projects_bp.route("/project/<int:project_id>/<string:slug>")
def project(project_id = None, slug=None):

    project = db.get_or_404(Project, project_id)

    expected_slug = slugify(project.title)

    if slug and slug != expected_slug:
        abort(404)

    return render_template(
        template_name_or_list='project.html',
        project=project,
        active_page='projects',
        meta_title=f"{project.author.name if project.author else 'Portfolio'} | {project.title}",
        meta_description=project.subtitle,
        meta_image=project.img_url,
        meta_type="website",
        robots_content=None
    )

@projects_bp.route("/new-project", methods=["GET", "POST"])
@admin_only
def add_new_project():

    form = CreateProjectForm()

    if form.validate_on_submit():

        try:
            new_project = Project(
                title=form.title.data,
                subtitle=form.subtitle.data,
                body=form.body.data,
                img_url=form.img_url.data,
                author=current_user,
                github_url=form.github_url.data,
                demo_url=form.demo_url.data,
                tags = ",".join(
                    [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
                ) if form.tags.data else ""

            )

            if form.hero_image.data:
                try:
                    src_url, _ = cloudinary_client.uploadImage(form.hero_image.data, folder="Projects", title=form.title.data)
                    new_project.img_url = src_url
                except Exception as e:
                    logger.error(f"Error uploading hero image: {e}")
                    flash(f"Error uploading hero image: {e}", "danger")

            db.session.add(new_project)
            db.session.commit()

        except IntegrityError as e:
            db.session.rollback()
            logger.exception(f"IntegrityError: {e}")
            flash(f"IntegrityError: {e}", "danger")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.exception(f"SQLAlchemyError: {e}")
            flash(f"SQLAlchemyError: {e}", "danger")
        else:
            flash("Project created successfully!", category="success")
            return redirect(url_for("projects.get_all_projects"))

    return render_template("make-content.html", form=form, is_edit=False, content_type="Project")


@projects_bp.route("/edit-project/<int:project_id>", methods=["GET", "POST"])
@admin_only
def edit_project(project_id = None):

    existing_project = db.get_or_404(Project, project_id)

    edit_form = CreateProjectForm(obj=existing_project)

    if edit_form.validate_on_submit():

        try:

            existing_project.title = edit_form.title.data
            existing_project.subtitle = edit_form.subtitle.data
            existing_project.img_url = edit_form.img_url.data

            if edit_form.hero_image.data:
                try:
                    src_url, _ = cloudinary_client.uploadImage(edit_form.hero_image.data, folder="Projects", title=edit_form.title.data)
                    existing_project.img_url = src_url
                except Exception as e:
                    logger.error(f"Error uploading hero image: {e}")
                    flash(f"Error uploading hero image: {e}", "danger")

            existing_project.github_url = edit_form.github_url.data
            existing_project.demo_url = edit_form.demo_url.data
            existing_project.tags = ','.join(
                [tag.strip() for tag in edit_form.tags.data.split(',') if tag.strip()]
            ) if edit_form.tags.data else ""
            existing_project.body = edit_form.body.data

            db.session.commit()

        except IntegrityError as e:
            db.session.rollback()
            logger.exception(f"IntegrityError: {e}")
            flash(message=f"IntegrityError: {e}", category="danger")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.exception(f"SQLAlchemyError: {e}")
            flash(f"SQLAlchemyError: {e}", "danger")
        else:
            flash("Project updated successfully!", category="success")
            return redirect(url_for("projects.project", project_id=existing_project.id))

    return render_template("make-content.html", form=edit_form, is_edit=True, content_type="Project")


@projects_bp.route("/delete-project/<int:project_id>", methods=["POST"])
@admin_only
def delete_project(project_id = None):

    existing_project = db.get_or_404(Project, project_id)

    try:
        name = existing_project.title
        db.session.delete(existing_project)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        logger.exception(f"IntegrityError: {e}")
        flash(message=f"IntegrityError: {e}", category="danger")
        return redirect(url_for("projects.project", project_id=existing_project.id))
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.exception(f"SQLAlchemyError: {e}")
        flash(f"SQLAlchemyError: {e}", "danger")
        return redirect(url_for("projects.project", project_id=existing_project.id))

    flash(f"Successfully deleted {name}!", category="success")
    return redirect(url_for("projects.get_all_projects"))


@sitemapper.include(lastmod=SITE_LASTMOD)
@projects_bp.route("/projects")
@projects_bp.route("/projects/<int:page>")
def get_all_projects(page = None):

    if page == 1:
        return redirect(url_for('projects.get_all_projects'), code=301)

    try:

        pagination = db.session.query(Project).order_by(Project.id.desc()).paginate(
            page=page or 1, per_page=6, error_out=False
        )
        project_list = pagination.items

        return render_template(
            template_name_or_list='projects.html',
            projects=project_list,
            pagination=pagination,
            active_page='projects'
        )

    except SQLAlchemyError as e:
        logger.exception(f"SQLAlchemyError: {e}")
        flash(message=f"SQLAlchemyError: {e}", category="danger")

    return render_template(
        template_name_or_list='projects.html',
        projects=None,
        pagination=None,
        active_page='projects'
    )