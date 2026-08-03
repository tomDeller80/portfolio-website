from forms import SetupForm, ContactForm, LoginForm, CreatePostForm, SkillForm, CreateProjectForm, UploadForm
from flask import Flask, render_template, flash, redirect, url_for, request, abort, send_from_directory
from flask_login import login_user, LoginManager, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError, InvalidRequestError, SQLAlchemyError
from wtforms.validators import Optional, Length, EqualTo
from database import User, Post, Project, Skill, Gallery, GalleryImage
from cloudinary import exceptions as cloudinary_exceptions
from datetime import date, datetime, timezone
from flask_sitemapper import Sitemapper
from flask_bootstrap import Bootstrap5
from cloudinary import CloudinaryImage
from flask_migrate import Migrate
from secrets import token_urlsafe
from extensions import db, mailer
from flask_quill import Quill
from images import Cloudinary
from functools import wraps
from sqlalchemy import func
from logger import Logger
import os, re

# Flask Security Key
FLASK_SECRET_KEY = (
    os.environ.get('FLASK_SECRET_KEY') or
    token_urlsafe(32)
)

# Site Last Mod
SITE_LASTMOD = os.environ.get("SITE_LASTMOD", date.today().isoformat())

# Setup Flask
app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)
bootstrap5 = Bootstrap5(app)
quill = Quill(app)
sitemapper = Sitemapper()
sitemapper.init_app(app)
migrate = Migrate(app, db)

# Flask Template Filters
@app.template_filter('format_date')
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


# Cloudinary Filter
@app.template_filter("cloudinary_thumb")
def cloudinary_thumb(public_id, width=480):
    return CloudinaryImage(public_id).build_url(
        width=width,
        crop="limit",
        quality="auto",
        fetch_format="auto",
        secure=True
    )


# Connect Database to App
uri = os.environ.get("DATABASE_URL") or os.environ.get("SQLALCHEMY_DATABASE_URI")

if not uri:
    # This ensures the app fails loudly if the database isn't configured
    raise ValueError("No DATABASE_URL or SQLALCHEMY_DATABASE_URI found in environment variables!")

if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
db.init_app(app)


# Create the tables
with app.app_context():
    db.create_all()

# Logger
logger = Logger(__name__).get_logger()

# Site Mapper Variable
def post_sitemap_vars():
    posts = db.session.query(Post).all()
    return {
        'post_id': [post.id for post in posts],
        'slug': [slugify(post.title) for post in posts]
    }

def post_sitemap_lastmod():
    posts = db.session.query(Post).all()
    return [
        (post.updated_at or post.created_at).date().isoformat() for post in posts
    ]

def project_sitemap_vars():
    projects = db.session.query(Project).all()
    return {
        'project_id': [project.id for project in projects],
        'slug': [slugify(project.title) for project in projects]
    }

def project_sitemap_lastmod():
    projects = db.session.query(Project).all()
    return [
        (project.updated_at or project.created_at).date().isoformat() for project in projects
    ]

# Flask Login Manager
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# Admin only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.is_admin or current_user.id != 1:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Post / Project titles into slugs
def slugify(text):
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[\s_-]+', '-', text)

# Flask Globals
@app.context_processor
def inject_globals():

    try:
        admin = db.session.query(User).where(
            User.id == 1 and User.is_admin == True
        ).scalar()

    except InvalidRequestError as e:
        logger.exception(f"An error occurred: {e}")
        flash(message=f"An error occurred: {e}", category="danger")

    return dict(
        date=date.today(),
        admin=admin if admin else None,
        slugify=slugify
    )

# Before Request
@app.before_request
def redirect_to_setup():

    allowed_endpoints = ['setup', 'static', 'login', 'logout', 'robots_txt']
    if request.endpoint in allowed_endpoints or not request.endpoint:
        return

    if request.path == url_for('setup') and request.method == 'POST':
        return

    try:

        admin_exists = db.session.query(User).filter(User.is_admin == True).first()

        if not admin_exists:
            logger.warning("No admin found in database. Redirecting to setup.")
            return redirect(url_for('setup'))

    except Exception as e:
        logger.error(f"Database check failed: {e}")
        return



# Flask Routing
@sitemapper.include(lastmod=SITE_LASTMOD)
@app.route("/")
def home():

    try:
        post = db.session.query(Post).order_by(Post.id.desc()).first()
        projects = db.session.query(Project).order_by(Project.id.desc()).all()
        skills = db.session.query(Skill).all()

    except InvalidRequestError as e:
        logger.exception(f"An error occurred: {e}")
        flash(f"An error occurred: {e}", category="danger")

    return render_template(
        template_name_or_list='index.html',
        projects=projects if projects else None,
        post = post if post else None,
        skills = skills if skills else None,
        active_page='home'
    )

@app.route("/robots.txt")
def robots_txt():
    return send_from_directory(directory="static", path="robots.txt", mimetype="text/plain")


@sitemapper.include(lastmod=SITE_LASTMOD)
@app.route("/about")
def about():

    try:
        skills = db.session.query(Skill).all()
    except InvalidRequestError as e:
        logger.exception(f"An error occurred: {e}")
        flash("An error occurred: {e}", category="danger")

    return render_template(
        template_name_or_list='about.html',
        active_page='about',
        skills = skills if skills else None
    )


@sitemapper.include(lastmod=SITE_LASTMOD)
@app.route("/contact", methods=['GET', 'POST'])
def contact():

    contact_form = ContactForm()

    if contact_form.validate_on_submit():

        response = mailer.send_email(
            email=contact_form.email.data,
            name=contact_form.name.data,
            subject=contact_form.subject.data,
            content=contact_form.message.data
        )

        if response["status_code"] >= 400:
            flash(message=response["text"], category="danger")
        else:
            flash(message="Your message has been successfully sent", category="success")
            return redirect(url_for('contact'))

    return render_template(
        template_name_or_list='contact.html',
        form=contact_form,
        active_page='contact'
    )


@sitemapper.include(url_variables=post_sitemap_vars, lastmod=post_sitemap_lastmod)
@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
@app.route("/post/<int:post_id>/<string:slug>", methods=['GET', 'POST'])
def post(post_id = None, slug = None):

    post = db.get_or_404(Post, post_id)

    expected_slug = slugify(post.title)

    if slug and slug != expected_slug:
        abort(404)

    return render_template(
        template_name_or_list='post.html',
        post=post,
        active_page='posts',
        slug=slug
    )



@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():

    form = CreatePostForm()

    if form.validate_on_submit():

        new_post = Post(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            tags=",".join([tag.strip() for tag in form.tags.data.split(',')]),
            author=current_user
        )

        try:

            db.session.add(new_post)
            db.session.commit()

        except IntegrityError as e:
            db.session.rollback()
            logger.exception(f"An error occurred: {e}")
            flash(f"An error occurred: {e}", "danger")
        else:
            flash("Post published successfully!", "success")
            return redirect(url_for('get_all_posts'))

    return render_template("make-content.html", form=form, is_edit=False, content_type="Post")


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id = None):

    existing_post = db.get_or_404(Post, post_id)

    edit_form = CreatePostForm(obj=existing_post)

    if edit_form.validate_on_submit():

        try:

            existing_post.title = edit_form.title.data
            existing_post.subtitle = edit_form.subtitle.data
            existing_post.img_url = edit_form.img_url.data
            existing_post.tags = ','.join(edit_form.tags.data.split(','))
            existing_post.body = edit_form.body.data


            db.session.commit()

        except IntegrityError as e:
            logger.exception(f"An error occurred: {e}")
            flash(message=f"An error occurred: {e}", category="danger")
        else:
            flash("Post updated successfully!", category="success")
            return redirect(url_for("post", post_id=existing_post.id))

    return render_template("make-content.html", form=edit_form, is_edit=True, content_type="Post")


@app.route("/delete-post/<int:post_id>")
@admin_only
def delete_post(post_id = None):

    existing_post = db.get_or_404(Post, post_id)

    try:

        name = existing_post.title
        db.session.delete(existing_post)
        db.session.commit()

    except IntegrityError as e:
        logger.exception(f"An error occurred: {e}")
        flash(message=f"An error occurred: {e}", category="danger")
        return redirect(url_for("post", post_id=existing_post.id))

    else:
        flash(f"Successfully deleted {name}!", category="success")
        return redirect(url_for("get_all_posts"))


@sitemapper.include(lastmod=SITE_LASTMOD)
@app.route("/posts")
@app.route("/posts/<int:page>", methods=['GET', 'POST'])
def get_all_posts(page = None):

    if page == 1:
        return redirect(url_for('get_all_posts'), code=301)

    try:
        pagination = db.session.query(Post).order_by(Post.id.desc()).paginate(
            page=page, per_page=6, error_out=False
        )
        post_list = pagination.items

        return render_template(
            template_name_or_list='posts.html',
            posts=post_list,
            pagination=pagination,
            active_page='posts'
        )

    except InvalidRequestError as e:
        logger.exception(f"InvalidRequestError: {e}")
        flash(message=f"InvalidRequestError: {e}", category="danger")

    return render_template(
        template_name_or_list='posts.html',
        posts=None,
        pagination=None,
        active_page='posts'
    )


@sitemapper.include(url_variables=project_sitemap_vars, lastmod=project_sitemap_lastmod)
@app.route("/project/<int:project_id>", methods=['GET', 'POST'])
@app.route("/project/<int:project_id>/<string:slug>", methods=['GET', 'POST'])
def project(project_id = None, slug=None):

    project = db.get_or_404(Project, project_id)

    expected_slug = slugify(project.title)

    if slug and slug != expected_slug:
        abort(404)

    return render_template(
        template_name_or_list='project.html',
        project=project,
        active_page='projects'
    )


@app.route("/new-project", methods=["GET", "POST"])
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
                tags=",".join([tag.strip() for tag in form.tags.data.split(',')])

            )
            db.session.add(new_project)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            logger.exception(f"An error occurred: {e}")
            flash(message=f"An error occurred: {e}", category="danger")
        else:
            flash("Project created successfully!", category="success")
            return redirect(url_for("get_all_projects"))

    return render_template("make-content.html", form=form, is_edit=False, content_type="Project")


@app.route("/edit-project/<int:project_id>", methods=["GET", "POST"])
@admin_only
def edit_project(project_id = None):

    existing_project = db.get_or_404(Project, project_id)

    edit_form = CreateProjectForm(obj=existing_project)

    if edit_form.validate_on_submit():

        try:

            existing_project.title = edit_form.title.data
            existing_project.subtitle = edit_form.subtitle.data
            existing_project.img_url = edit_form.img_url.data
            existing_project.github_url = edit_form.github_url.data
            existing_project.demo_url = edit_form.demo_url.data
            existing_project.tags = ','.join(edit_form.tags.data.split(','))
            existing_project.body = edit_form.body.data,


            db.session.commit()

        except IntegrityError as e:
            logger.exception(f"An error occurred: {e}")
            flash(message=f"An error occurred: {e}", category="danger")
        else:
            flash("Project updated successfully!", category="success")
            return redirect(url_for("project", project_id=existing_project.id))

    return render_template("make-content.html", form=edit_form, is_edit=True, content_type="Project")



@app.route("/delete-project/<int:project_id>")
@admin_only
def delete_project(project_id = None):

    existing_project = db.get_or_404(Project, project_id)

    try:

        name = existing_project.title
        db.session.delete(existing_project)
        db.session.commit()

    except IntegrityError as e:
        logger.exception(f"An error occurred: {e}")
        flash(message=f"An error occurred: {e}", category="danger")
        return redirect(url_for("project", post_id=existing_project.id))
    else:
        flash(f"Successfully deleted {name}!", category="success")
        return redirect(url_for("get_all_projects"))


@sitemapper.include(lastmod=SITE_LASTMOD)
@app.route("/projects")
@app.route("/projects/<int:page>", methods=['GET', 'POST'])
def get_all_projects(page = None):

    if page == 1:
        return redirect(url_for('get_all_projects'), code=301)

    try:

        pagination = db.session.query(Project).order_by(Project.id.desc()).paginate(
            page=page, per_page=6, error_out=False
        )
        project_list = pagination.items

        return render_template(
            template_name_or_list='projects.html',
            projects=project_list,
            pagination=pagination,
            active_page='projects'
        )

    except InvalidRequestError as e:
        logger.exception(f"InvalidRequestError: {e}")
        flash(message=f"InvalidRequestError: {e}", category="danger")

    return render_template(
        template_name_or_list='projects.html',
        posts=None,
        pagination=None,
        active_page='projects'
    )

@app.route("/add-skill", methods=["GET", "POST"])
@admin_only # Assuming you have a decorator for admin access
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
            logger.exception(f"An error occurred: {e}")
            flash(message=f"An error occurred: {e}", category="danger")
        else:
            flash(f"Successfully added {new_skill.name}!", "success")
            return redirect(url_for('home'))

    return render_template("add_skills.html", form=form)


@app.route("/delete-skill/<int:skill_id>")
@admin_only
def delete_skill(skill_id):

    skill_to_delete = db.get_or_404(Skill, skill_id)

    name = skill_to_delete.name
    db.session.delete(skill_to_delete)
    db.session.commit()

    flash(f"{name} has been removed from your tech stack.", "info")
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        flash(message='You are already signed in.', category='success')
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(message='You have been successfully logged in.', category='success')
            return redirect(url_for('home'))
        else:
            flash(message='Invalid email or password.', category='danger')

    return render_template(template_name_or_list='login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash(message='You have been successfully logged out.', category='success')
    return redirect(url_for('home'))


@app.route('/setup', methods=['GET', 'POST'])
def setup():

    try:

        existing_admin = db.session.query(User).filter(
                             User.is_admin == True and User.id == 1
                         ).scalar()

        if existing_admin:
            flash( message="Setup already completed. Please log in.", category="info")
            return redirect(url_for('login'))

    except InvalidRequestError as e:
        logger.exception(f"An error occurred: {e} ")
        flash("An error occurred: {e}", category="danger")

    form = SetupForm()

    if form.validate_on_submit():

        hashed_pw = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )

        try:

            is_admin_value = form.is_admin.data == 'True'

            new_admin = User(
                name=form.name.data,
                email=form.email.data,
                password=hashed_pw,
                job_title=form.job_title.data,
                pronoun=form.pronoun.data,
                tagline=form.tagline.data,
                about=form.about.data,
                location=form.location.data,
                profile_img=form.profile_img.data,
                resume_url = form.resume_url.data,
                linkedin=form.linkedin.data,
                github=form.github.data,
                is_admin = is_admin_value
            )

            db.session.add(new_admin)
            db.session.commit()

        except IntegrityError as e:
            logger.exception(f"IntegrityError: {e}")
            flash(message=f"IntegrityError: {e}", category="danger")

        flash("Admin account created successfully! You can now log in.", "success")
        return redirect(url_for('login'))

    else:
        if request.method == 'POST':
            logger.error(f"Form Validation Failed! Errors: {form.errors}")

    return render_template(template_name_or_list="setup.html", form=form, admin=None)


@app.route("/edit-profile", methods=["GET", "POST"])
@admin_only
def edit_profile():

    admin_user = db.get_or_404(User, 1)

    form = SetupForm(obj=admin_user)

    if admin_user:
        form.password.validators = [Optional(), Length(min=8)]
        form.confirm_password.validators = [Optional(), EqualTo('password')]

    if form.validate_on_submit():

        try:

            admin_user.name = form.name.data
            admin_user.email = form.email.data

            if form.password.data:
                admin_user.password = generate_password_hash(
                    form.password.data,
                    method='pbkdf2:sha256',
                    salt_length=8
                )

            admin_user.job_title = form.job_title.data
            admin_user.pronoun = form.pronoun.data
            admin_user.tagline = form.tagline.data
            admin_user.about = form.about.data
            admin_user.location = form.location.data
            admin_user.profile_img = form.profile_img.data
            admin_user.resume_url = form.resume_url.data
            admin_user.linkedin = form.linkedin.data
            admin_user.github = form.github.data


            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for('home'))

        except IntegrityError as e:

            logger.exception(f"An error occurred: {e}")
            flash(message=f"An error occurred: {e}", category="danger")

    else:
        if request.method == 'POST':
            logger.error(f"Form Validation Failed! Errors: {form.errors}")


    return render_template("setup.html", form=form, admin=admin_user)

@app.route("/upload/<string:target_type>/<int:target_id>", methods=["GET", "POST"])
@admin_only
def upload(target_type=None, target_id=None):

    if target_type == "post":
        target = db.get_or_404(Post, target_id)
        folder = "Posts"
        gallery = Gallery.query.filter_by(post_id=target.id).first()
        gallery_kwargs = {"post_id": target.id}
        cancel_url = url_for("post", post_id=target.id)
    elif target_type == "project":
        target = db.get_or_404(Project, target_id)
        folder = "Projects"
        gallery = Gallery.query.filter_by(project_id=target.id).first()
        gallery_kwargs = {"project_id": target.id}
        cancel_url = url_for("project", project_id=target.id)
    else:
        abort(404)

    form = UploadForm()

    if form.validate_on_submit():

        file = form.file.data

        kwargs = {
            'title': form.title.data,
            'alt': form.alt.data,
            'folder': folder,
            'tags': [tag.strip() for tag in form.tags.data.split(",") if tag.strip()] if form.tags.data else []
        }

        try:
            cloudinary = Cloudinary()
            src_url, public_id = cloudinary.uploadImage(file, **kwargs)
        except ValueError as e:
            logger.warning(f"Upload validation failed: {e}")
            flash(message=str(e), category="danger")
        except cloudinary_exceptions.Error as e:
            logger.exception(f"Cloudinary upload failed: {e}")
            flash(message="Image upload failed. Please check the upload service configuration.", category="danger")
        except Exception as e:
            logger.exception(f"Unexpected upload error: {e}")
            flash(message="An unexpected error occurred while uploading the image.", category="danger")
        else:

            try:
                # Create Gallery if none exists
                if not gallery:
                    gallery = Gallery(**gallery_kwargs)
                    db.session.add(gallery)
                    db.session.flush()

                # Acquire Next Gallery Position
                next_position = (
                    db.session.query(func.coalesce(func.max(GalleryImage.position), -1) + 1)
                    .filter(GalleryImage.gallery_id == gallery.id)
                    .scalar()
                )

                # 2. Create GalleryImage and assign to Gallery by id
                gallery_image = GalleryImage(
                    gallery_id=gallery.id,
                    public_id=public_id,
                    url=src_url,
                    title=form.title.data,
                    description=form.description.data,
                    tags=",".join(kwargs["tags"]),
                    alt_text=form.alt.data,
                    position=next_position
                )

                db.session.add(gallery_image)
                db.session.commit()

            except SQLAlchemyError as e:

                db.session.rollback()
                logger.exception(f"Database upload save failed: {e}")
                flash(message="Image uploaded, but saving the gallery record failed.", category="danger")
                return render_template(
                    "upload.html",
                    form=form,
                    src_url=src_url,
                    target_type=target_type,
                    target_id=target_id,
                    target=target,
                    cancel_url=cancel_url
                )

            else:

                flash(message="Image uploaded successfully!", category="success")

                if target_type == "post":
                    return redirect(url_for("post", post_id=target_id))
                elif target_type == "project":
                    return redirect(url_for("project", project_id=target_id))
                else:
                   return render_template(
                      "upload.html",
                      form=form,
                      src_url=src_url,
                      target_type=target_type,
                      target_id=target_id,
                      target=target,
                      cancel_url=cancel_url
                   )


    elif request.method == 'POST':
        flash(message="Upload form validation failed!", category="danger")
        logger.warning(f"Upload form validation failed: {form.errors}")

    return render_template(
        "upload.html",
        form=form,
        target_type=target_type,
        target_id=target_id,
        target=target,
        cancel_url=cancel_url
    )


@app.route("/sitemap.xml")
def sitemap():
  return sitemapper.generate()

if __name__ == "__main__":
    app.run(debug=False)
