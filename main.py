from forms import SetupForm, ContactForm, LoginForm, CreatePostForm, SkillForm, CreateProjectForm
from flask import Flask, render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, LoginManager, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from wtforms.validators import Optional, Length, EqualTo
from database import User, Post, Project, Skill
from flask_bootstrap import Bootstrap5
from secrets import token_urlsafe
from functools import wraps
from flask_quill import Quill
from datetime import date
from extensions import db, mailer
from logger import Logger
import os

# Flask Security Key
FLASK_SECRET_KEY = (
    os.environ.get('FLASK_SECRET_KEY') or
    token_urlsafe(32)
)

# Setup Flask
app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)
bootstrap5 = Bootstrap5(app)
quill = Quill(app)


# Connect Database to App
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL','sqlite:///posts.db')
)
db.init_app(app)

# Create the tables
with app.app_context():
    db.create_all()

# Logger
logger = Logger(__name__).get_logger()

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
        elif current_user.is_admin == True and current_user.id != 1:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

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
    )

# Before Request
@app.before_request
def redirect_to_setup():

    allowed_endpoints = ['setup', 'static', 'login', 'logout']
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
@app.route("/")
def home():

    try:

        post = db.session.query(Post).order_by(Post.id.desc()).first()
        projects = db.session.query(Project).order_by(Project.date.desc()).all()
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


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id = None):

    post = db.get_or_404(Post, post_id)

    return render_template(
        template_name_or_list='post.html',
        post=post,
        active_page='posts'
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
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
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


@app.route("/posts")
@app.route("/posts/<int:page>", methods=['GET', 'POST'])
def get_all_posts(page = None):

    try:

        pagination = db.session.query(Post).order_by(Post.date.desc()).paginate(
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


@app.route("/project/<int:project_id>", methods=['GET', 'POST'])
def project(project_id = None):
    project = db.get_or_404(Project, project_id)

    return render_template(
        template_name_or_list='project.html',
        project=project,
        active_page='posts'
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
                tags=",".join([tag.strip() for tag in form.tags.data.split(',')]),
                date=date.today().strftime("%B %d, %Y")
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
            existing_project.body = edit_form.body.data

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


@app.route("/projects")
@app.route("/projects/<int:page>", methods=['GET', 'POST'])
def get_all_projects(page = None):
    try:

        pagination = db.session.query(Project).order_by(Project.date.desc()).paginate(
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


if __name__ == "__main__":
    app.run(debug=False)