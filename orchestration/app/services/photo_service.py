import os
import uuid
from azure.storage.blob import BlobServiceClient


class PhotoService:
    def __init__(self):
        self._conn_str = os.environ.get(
            'AZURITE_CONNECTION_STRING',
            'DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;'
            'AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq'
            '/K1SZFPTOtr/KBHBeksoGMGw==;'
            'BlobEndpoint=http://azurite:10000/devstoreaccount1;'
        )
        self.container_name = os.environ.get('AZURITE_CONTAINER_NAME', 'photos')
        self._blob_service = None

    @property
    def blob_service(self):
        if self._blob_service is None:
            self._blob_service = BlobServiceClient.from_connection_string(self._conn_str)
        return self._blob_service

    def _ensure_container(self):
        try:
            container_client = self.blob_service.get_container_client(self.container_name)
            container_client.get_container_properties()
        except Exception:
            self.blob_service.create_container(self.container_name)

    def upload_photo(self, file_data, filename=None):
        if filename is None:
            filename = f'{uuid.uuid4().hex}.jpg'

        self._ensure_container()
        blob_client = self.blob_service.get_blob_client(
            container=self.container_name,
            blob=filename
        )
        blob_client.upload_blob(file_data, overwrite=True)
        return blob_client.url

    def delete_photo(self, photo_url):
        if not photo_url:
            return
        try:
            filename = photo_url.rsplit('/', 1)[-1]
            blob_client = self.blob_service.get_blob_client(
                container=self.container_name,
                blob=filename
            )
            blob_client.delete_blob()
        except Exception:
            pass
