import os
import logging
import requests

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.base_url = os.getenv("NTFY_BASE_URL")
        if not self.base_url:
            raise ValueError("NTFY_BASE_URL must be set")

    # makes http call to the ntfy to send the push notication.
    def SendPushNotification(self, topic_name: str, title: str, payload: str):
        url = f"{self.base_url}/{topic_name}"
        headers = {
            "Title": title.encode("utf-8").decode("latin-1"),
            "Priority": "urgent",
            "Content-Type": "text/plain"
        }
        try:
            response = requests.post(url, headers=headers, data=payload.encode("utf-8"))
            response.raise_for_status()
            logger.info("Push notification sent to topic '%s'. Status: %s", topic_name, response.status_code)
        except Exception as e:
            logger.error("Failed to send push notification to topic '%s': %s", topic_name, e)
