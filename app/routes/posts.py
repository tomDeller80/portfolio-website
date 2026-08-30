from flask import Blueprint, render_template, flash, url_for, redirect, abort
from .sitemap import post_sitemap_vars, post_sitemap_lastmod, SITE_LASTMOD
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.extensions import sitemapper, db, cloudinary_client
from flask_login import current_user
from app.forms import CreatePostForm
from app.decorators import admin_only
from app.helpers import slugify
from app.database import Post
from app.logger import Logger


logger = Logger(__name__).get_logger()

posts_bp = Blueprint('posts', __name__)

@sitemapper.include(url_variables=post_sitemap_vars, lastmod=post_sitemap_lastmod)
@posts_bp.route("/post/<int:post_id>")
@posts_bp.route("/post/<int:post_id>/<string:slug>")
def post(post_id = None, slug = None):

    post = db.get_or_404(Post, post_id)

    expected_slug = slugify(post.title)

    if slug and slug != expected_slug:
        abort(404)

    return render_template(
        template_name_or_list='post.html',
        post=post,
        active_page='posts',
        slug=slug,
        meta_title=f"{post.author.name if post.author else 'Portfolio'} | {post.title}",
        meta_description=post.subtitle,
        meta_image=post.img_url,
        meta_type="article",
        robots_content=None
    )

@posts_bp.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():

    form = CreatePostForm()

    if form.validate_on_submit():

        new_post = Post(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            tags=",".join([tag.strip() for tag in form.tags.data.split(',') if tag.strip()]) if form.tags.data else "",
            author=current_user
        )

        if form.hero_image.data:
            try:
                src_url, _ = cloudinary_client.uploadImage(form.hero_image.data, folder="Posts", title=form.title.data)
                new_post.img_url = src_url
            except Exception as e:
                logger.error(f"Error uploading hero image: {e}")
                flash(f"Error uploading hero image: {e}", "danger")

        try:
            db.session.add(new_post)
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
            flash("Post published successfully!", "success")
            return redirect(url_for('posts.get_all_posts'))

    return render_template("make-content.html", form=form, is_edit=False, content_type="Post")


@posts_bp.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id = None):

    existing_post = db.get_or_404(Post, post_id)

    edit_form = CreatePostForm(obj=existing_post)

    if edit_form.validate_on_submit():

        try:

            existing_post.title = edit_form.title.data
            existing_post.subtitle = edit_form.subtitle.data
            existing_post.img_url = edit_form.img_url.data
            
            if edit_form.hero_image.data:
                try:
                    src_url, _ = cloudinary_client.uploadImage(edit_form.hero_image.data, folder="Posts", title=edit_form.title.data)
                    existing_post.img_url = src_url
                except Exception as e:
                    logger.error(f"Error uploading hero image: {e}")
                    flash(f"Error uploading hero image: {e}", "danger")

            existing_post.tags = ','.join(
                [tag.strip() for tag in edit_form.tags.data.split(',') if tag.strip()]
            ) if edit_form.tags.data else ""
            existing_post.body = edit_form.body.data

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
            flash("Post updated successfully!", category="success")
            return redirect(url_for("posts.post", post_id=existing_post.id))

    return render_template("make-content.html", form=edit_form, is_edit=True, content_type="Post")


@posts_bp.route("/delete-post/<int:post_id>", methods=["POST"])
@admin_only
def delete_post(post_id = None):

    existing_post = db.get_or_404(Post, post_id)

    try:
        name = existing_post.title
        db.session.delete(existing_post)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        logger.exception(f"IntegrityError: {e}")
        flash(message=f"IntegrityError: {e}", category="danger")
        return redirect(url_for("posts.post", post_id=existing_post.id))
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.exception(f"SQLAlchemyError: {e}")
        flash(f"SQLAlchemyError: {e}", "danger")
        return redirect(url_for("posts.post", post_id=existing_post.id))

    flash(f"Successfully deleted {name}!", category="success")
    return redirect(url_for("posts.get_all_posts"))


@sitemapper.include(lastmod=SITE_LASTMOD)
@posts_bp.route("/posts")
@posts_bp.route("/posts/<int:page>")
def get_all_posts(page = None):

    if page == 1:
        return redirect(url_for('posts.get_all_posts'), code=301)

    try:
        pagination = db.session.query(Post).order_by(Post.id.desc()).paginate(
            page=page or 1, per_page=6, error_out=False
        )
        post_list = pagination.items

        return render_template(
            template_name_or_list='posts.html',
            posts=post_list,
            pagination=pagination,
            active_page='posts'
        )

    except SQLAlchemyError as e:
        logger.exception(f"SQLAlchemyError: {e}")
        flash(message=f"SQLAlchemyError: {e}", category="danger")

    return render_template(
        template_name_or_list='posts.html',
        posts=None,
        pagination=None,
        active_page='posts'
    )