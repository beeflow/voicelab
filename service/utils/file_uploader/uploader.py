from django.core.files.uploadedfile import InMemoryUploadedFile

from utils.translator import translate

from vl_server import settings
from .uploaders.local_uploader import LocalUploader
from .uploaders.s3_uploader import S3Uploader


class UploaderError(RuntimeError):
    pass


class Uploader:
    __uploaders = {
        's3': S3Uploader,
        'local': LocalUploader
    }

    def __init__(self):
        try:
            self.__uploader = self.__uploaders[settings.UPLOADER]()
        except KeyError:
            raise UploaderError(f"{translate('There is no such uploader like')} {settings.UPLOADER}")

    def upload(self, source_path, destination_path):
        self.__uploader.upload(source_path, destination_path)

    def upload_in_memory_uploaded_file(self, image: InMemoryUploadedFile, directory: str, filename: str) -> None:
        self.__uploader.upload_in_memory_uploaded_file(image, directory, filename)

    def delete(self, filename: str) -> None:
        self.__uploader.delete(filename)
