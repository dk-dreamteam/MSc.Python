import os
import uuid
import logging
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger(__name__)


class PhotoBlobService:
    def __init__(self):
        conn_str = os.getenv("AZURITE_BLOB_CONNECTION_STRING")
        if not conn_str:
            raise ValueError("AZURITE_BLOB_CONNECTION_STRING must be set")
        
        self.container_name = os.getenv("BLOB_CONTAINER_NAME")
        if not self.container_name:
            raise ValueError("BLOB_CONTAINER_NAME must be set")

        self.client = BlobServiceClient.from_connection_string(conn_str)
        self._ensure_container()

    def _ensure_container(self):
        try:
            self.client.get_container_client(self.container_name).get_container_properties()
        except Exception:
            self.client.create_container(self.container_name)
            logger.info("Created container '%s'", self.container_name)

    def upload(self, file_data: bytes, original_filename: str) -> str:
        blob_name = f"{uuid.uuid4()}_{original_filename}"
        blob_client = self.client.get_blob_client(container=self.container_name, blob=blob_name)
        blob_client.upload_blob(file_data, overwrite=True)
        logger.info("Uploaded blob '%s'", blob_name)
        return blob_name

    def download(self, blob_name: str) -> bytes:
        blob_client = self.client.get_blob_client(container=self.container_name, blob=blob_name)
        return blob_client.download_blob().readall()
