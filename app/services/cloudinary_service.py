import os
import cloudinary.uploader
import cloudinary.api
import cloudinary

class CloudinaryService:

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


    def deleteImage(self, public_id):

        if not public_id:
            return None

        return cloudinary.uploader.destroy(public_id)