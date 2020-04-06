from rest_framework.parsers import FileUploadParser


class ImageUploadParser(FileUploadParser):
    """Parser for image upload data.

    Used to parse the content of the reqest by Django REST Framework.
    """
    media_type = 'image/*'
