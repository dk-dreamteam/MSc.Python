import json
import logging
import os
from azure.storage.queue import QueueClient

logger = logging.getLogger(__name__)


class QueueSenderService:
    def __init__(self):
        conn_str = os.getenv("AZURITE_CONNECTION_STRING")
        if not conn_str:
            raise ValueError("AZURITE_CONNECTION_STRING must be set")
        self.conn_str = conn_str

    def _send(self, queue_name: str, message: dict):
        queue_client = QueueClient.from_connection_string(self.conn_str, queue_name)
        queue_client.send_message(json.dumps(message, ensure_ascii=False))
        logger.info("Message sent to queue '%s'", queue_name)

    def send_notification(self, topic_name: str, title: str, payload: str, attach_url: str = None):
        queue_name = os.getenv("NOTIFICATIONS_QUEUE_NAME")
        if not queue_name:
            raise ValueError("NOTIFICATIONS_QUEUE_NAME must be set")
        
        message = {"topic_name": topic_name, "title": title, "payload": payload}
        if attach_url:
            message["attach_url"] = attach_url

        self._send(queue_name, message)

    def send_for_preprocessing(self, id: str, text: str, address: str):
        queue_name = os.getenv("PREPROCESSOR_QUEUE_NAME")
        if not queue_name:
            raise ValueError("PREPROCESSOR_QUEUE_NAME must be set")
        
        message = {"id": id, "text": text, "address": address}
        
        self._send(queue_name, message)
