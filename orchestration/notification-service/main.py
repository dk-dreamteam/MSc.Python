import os
import time
import json
import logging
from azure.storage.queue import QueueClient
from azure.core.exceptions import ResourceNotFoundError
from notification_service import NotificationService

# prepare logger.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# silence Azure SDK logs
for _logger in ["azure", "azure.core", "azure.storage", "urllib3"]:
    logging.getLogger(_logger).setLevel(logging.WARNING)

# get env vars.
QUEUE_NAME = os.getenv("QUEUE_NAME")
CONNECTION_STRING = os.getenv("AZURITE_CONNECTION_STRING")

# create queue storage client.
def get_queue_client() -> QueueClient:
    return QueueClient.from_connection_string(CONNECTION_STRING, QUEUE_NAME)

# check if the queue exists. if not create it.
def ensure_queue(queue_client):
    try:
        properties = queue_client.get_queue_properties()
        logger.info("Queue '%s' already exists.", QUEUE_NAME)
    except ResourceNotFoundError:
        logger.info("Queue '%s' not found. Creating...", QUEUE_NAME)
        queue_client.create_queue()
        logger.info("Queue '%s' created.", QUEUE_NAME)

# "subscribe" to the queue and start processing messages.
def poll_messages(queue_client):
    logger.info("Listening for messages on queue '%s'...", QUEUE_NAME)
    while True:
        messages = queue_client.receive_messages(max_messages=32, visibility_timeout=30)
        for message in messages:
            
            # try deserialize. if the payload is corrupted, skip and delete the message from the queue.
            try:
                data = json.loads(message.content)
                notification_service.SendPushNotification(
                    topic_name=data.get("topic_name"),
                    title=data.get("title"),
                    payload=data.get("payload"),
                )
            except Exception as e:
                logger.error("Failed to process message: %s", e)
                
            queue_client.delete_message(message)
        time.sleep(1)

#if queuename and conneciton string are not provided, throw exception.
if not QUEUE_NAME or not CONNECTION_STRING:
    raise ValueError("QUEUE_NAME and AZURITE_CONNECTION_STRING must be set")

notification_service = NotificationService()

# execute.
queue_client = get_queue_client()
ensure_queue(queue_client)
poll_messages(queue_client)
