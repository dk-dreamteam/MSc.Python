import os
import logging
import requests

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.base_url = os.getenv("NTFY_BASE_URL")
        if not self.base_url:
            raise ValueError("NTFY_BASE_URL must be set")

    def SendPushNotification(self, topic_name: str, title: str, payload: str, attach_url: str):
        url = f"{self.base_url}/{topic_name}"
        headers = {
            "Title": title,
            "Priority": "urgent",
            "Attach": attach_url,
            "Content-Type": "text/plain"
        }
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        logger.info("Push notification sent to opic '%s'. Status: %s", topic_name, response.status_code)
