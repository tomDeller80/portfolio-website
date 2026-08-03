import os
from cloudinary import CloudinaryImage
import cloudinary.uploader
import cloudinary.api
import cloudinary

# Environment variables
api_key = os.environ.get('CLOUDINARY_KEY')
api_secret = os.environ.get('CLOUDINARY_SECRET')
CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD')

if not api_key or not api_secret:
    raise ValueError("Cloudinary credentials are not configured")

# Configure globally at module import time
cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=api_key,
    api_secret=api_secret,
    secure=True
)

class Cloudinary:

    def __init__(self):

        self.allowed_extensions = {"png", "jpg", "jpeg"}

    def file_checker(self, filename):
        return ("." in filename and filename.rsplit(".", 1)[1].lower() in self.allowed_extensions)

    def file_base_name(self, image):
        image_name = getattr(image, "filename", image)
        file_basename = os.path.basename(image_name)
        file_name =  os.path.splitext(file_basename)[0]

        return (file_name, file_basename)

    def uploadImage(self, image, unique_filename=False, overwrite=True, **kwargs):

        # Name of file without extension
        file_name, file_basename = self.file_base_name(image)

        # Check if file extension is valid
        if not self.file_checker(file_basename):
            raise ValueError("Invalid file extension")

        # Get additional kwargs
        public_id = kwargs.get("title", file_name if file_name else None)
        alt = kwargs.get("alt", None)
        tags = kwargs.get("tags", None)
        folder = kwargs.get("folder", None)


        # Upload the image
        upload_result = cloudinary.uploader.upload(
            image,
            public_id=public_id,
            tags=tags,
            unique_filename=unique_filename,
            overwrite=overwrite,
            folder=folder,
            context={
                "alt": alt,
                "caption": public_id
            }
        )

        return (upload_result["secure_url"], upload_result["public_id"])


    def addTags(self, file_name, tags=None):
        if tags is None:
            tags = []

        image_info = cloudinary.api.resource(file_name)
        original_tags = image_info.get("tags", [])
        current_tags = list(original_tags)
        update_resp = image_info

        for tag in tags:
            if tag not in current_tags:
                current_tags.append(tag)

        if current_tags != original_tags:
            update_resp = cloudinary.api.update(file_name, tags=current_tags)

        return update_resp.get("tags", current_tags)

    def imageResize(self, file_name, width=150, height=150, crop="fill"):

        transformedURL = CloudinaryImage(file_name).build_url(
            width=width,
            height=height,
            crop=crop)

        return transformedURL
