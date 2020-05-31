import os

from django.core.files.uploadedfile import InMemoryUploadedFile

from vl_server import settings


class LocalUploader:
    def __init__(self):
        self.__base_dir = settings.UPLOAD_DIR

    def upload(self, source_path, destination_path):
        pass

    def upload_in_memory_uploaded_file(self, uploaded_file: InMemoryUploadedFile, directory: str, filename: str) -> None:
        self.__create_directory(directory)
        with open(f'{self.__base_dir}/{directory}/{filename}', 'wb+') as file:
            for chunk in uploaded_file.chunks():
                file.write(chunk)

    def delete(self, filename: str) -> None:
        if os.path.isfile(f'{self.__base_dir}/{filename}'):
            os.remove(f'{self.__base_dir}/{filename}')

    def __create_directory(self, folder_name: str) -> None:
        try:
            os.makedirs(f'{self.__base_dir}/{folder_name}/')
        except OSError:
            pass
