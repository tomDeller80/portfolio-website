from flask import Blueprint, request, url_for, redirect, flash, render_template, abort
from cloudinary import exceptions as cloudinary_exceptions
from app.database import Post, Project, Gallery, GalleryImage
from app.extensions import db, cloudinary_client
from sqlalchemy.exc import SQLAlchemyError
from app.decorators import admin_only
from app.forms import UploadForm
from app.logger import Logger
from sqlalchemy import func


logger = Logger(__name__).get_logger()
media_bp = Blueprint('media', __name__)

@media_bp.route("/upload/<string:target_type>/<int:target_id>", methods=["GET", "POST"])
@admin_only
def upload(target_type=None, target_id=None):
    usage = request.args.get('usage', 'gallery')

    if target_type == "post":
        target = db.get_or_404(Post, target_id)
        folder = "Posts"
        gallery = db.session.query(Gallery).filter_by(post_id=target.id).first()
        gallery_kwargs = {"post_id": target.id}
        cancel_url = url_for("posts.post", post_id=target.id)
    elif target_type == "project":
        target = db.get_or_404(Project, target_id)
        folder = "Projects"
        gallery = db.session.query(Gallery).filter_by(project_id=target.id).first()
        gallery_kwargs = {"project_id": target.id}
        cancel_url = url_for("projects.project", project_id=target.id)
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
            src_url, public_id = cloudinary_client.uploadImage(file, **kwargs)
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
                if usage == "hero":
                    target.img_url = src_url
                else:
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

                try:
                    cloudinary_client.deleteImage(public_id)
                except Exception as cleanup_err:
                    logger.error(f"Failed to cleanup orphaned Cloudinary image {public_id}: {cleanup_err}")

                logger.exception(f"Database upload save failed: {e}")
                flash(message="Image uploaded, but saving the record failed.", category="danger")
                return render_template(
                    "upload.html",
                    form=form,
                    src_url=src_url,
                    target_type=target_type,
                    target_id=target_id,
                    target=target,
                    cancel_url=cancel_url,
                    usage=usage
                )

            else:

                flash(message=f"{'Hero image' if usage == 'hero' else 'Gallery image'} uploaded successfully!", category="success")

                if target_type == "post":
                    return redirect(url_for("posts.post", post_id=target_id))
                elif target_type == "project":
                    return redirect(url_for("projects.project", project_id=target_id))
                else:
                   return render_template(
                      "upload.html",
                      form=form,
                      src_url=src_url,
                      target_type=target_type,
                      target_id=target_id,
                      target=target,
                      cancel_url=cancel_url,
                      usage=usage
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
        cancel_url=cancel_url,
        usage=usage
    )


@media_bp.route("/delete-image/<string:target_type>/<int:target_id>/<path:public_id>", methods=["POST"])
@admin_only
def delete_image(target_type, target_id, public_id):



    image = db.session.query(GalleryImage).filter(GalleryImage.public_id == public_id).first()

    if not image:
        flash("Image record not found in database.", category="danger")
    else:

        try:
            cloudinary_client.deleteImage(public_id)

        except cloudinary_exceptions.Error as e:
            flash(message="Error deleting image from cloudinary!", category="danger")
            logger.error(f"Error deleting image: {e}")

        except Exception as e:
            flash(message="Error deleting image!", category="danger")
            logger.error(f"Error deleting image: {e}")

        else:

            try:
                db.session.delete(image)
                db.session.commit()

                flash(message=f"Image removed from database: {public_id}", category="success")
                logger.info(f"Image removed from database: {public_id}")

            except SQLAlchemyError as e:

                db.session.rollback()
                flash(message="Error deleting image!", category="danger")
                logger.error(f"Error deleting image: {e}")

    if target_type == "post":
        return redirect(url_for("posts.post", post_id=target_id))
    elif target_type == "project":
        return redirect(url_for("projects.project", project_id=target_id))
    else:
        return redirect(url_for("main.home"))