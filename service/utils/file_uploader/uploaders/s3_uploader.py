import boto3
from django.core.files.uploadedfile import InMemoryUploadedFile
from s3transfer import S3Transfer

from vl_server import settings


class S3Uploader:
    @staticmethod
    def __get_s3_resource():
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        return session.resource('s3')

    @staticmethod
    def upload(local_path, s3_path):
        transfer = S3Transfer(boto3.client(
            's3', settings.AWS_S3_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        )
        transfer.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, s3_path)

    def upload_in_memory_uploaded_file(self, image: InMemoryUploadedFile, directory: str, filename: str) -> None:
        s3 = self.__get_s3_resource()
        s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).put_object(Key=f'static/{directory}/%s' % filename, Body=image)

    def delete(self, filename: str) -> None:
        s3 = self.__get_s3_resource()
        s3.Object(settings.AWS_STORAGE_BUCKET_NAME, f'static/{filename}')
