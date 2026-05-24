import os
import time
import json
import logging
from azure.storage.queue import QueueClient
from azure.core.exceptions import ResourceNotFoundError
from llm_classifier import LLMClassifierService
from geo_service import GeoService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

for _logger in ["azure", "azure.core", "azure.storage", "urllib3"]:
    logging.getLogger(_logger).setLevel(logging.WARNING)

QUEUE_NAME = os.getenv("QUEUE_NAME")
CONNECTION_STRING = os.getenv("AZURITE_CONNECTION_STRING")


def get_queue_client() -> QueueClient:
    return QueueClient.from_connection_string(CONNECTION_STRING, QUEUE_NAME)


def ensure_queue(queue_client):
    try:
        properties = queue_client.get_queue_properties()
        logger.info("Queue '%s' already exists.", QUEUE_NAME)
    except ResourceNotFoundError:
        logger.info("Queue '%s' not found. Creating...", QUEUE_NAME)
        queue_client.create_queue()
        logger.info("Queue '%s' created.", QUEUE_NAME)


def process_messages(queue_client: QueueClient, llm_service: LLMClassifierService, geo_service: GeoService):
    logger.info("Listening for messages on queue '%s'...", QUEUE_NAME)
    while True:
        # start listening.
        messages = queue_client.receive_messages(max_messages=32, visibility_timeout=30)
        for message in messages:
            try:
                # json deserialize.
                data = json.loads(message.content)

                # job1: Fetch ticket from database.
                # todo:

                # job2: Communicate with LLM to get the description classification.
                category_id = llm_service.Classify(data.get("text", "Αυτο δεν ειναι κάτι σοβαρό."))

                # job3: Communicate with OpenStreetMap nominatim to get the lat long from the address.
                lat, lon = geo_service.GetCoordinatesFromAddress(data.get("address", "Κρήτης 29, Αγία Βαρβάρα"))

                # job4: Update the ticket in the database with updated values.
                logger.info("Processed: category=%d, lat=%f, lon=%f", category_id, lat, lon)
            except Exception as e:
                logger.error("Failed to process message: %s", e)
            queue_client.delete_message(message)
        time.sleep(1)


if not QUEUE_NAME or not CONNECTION_STRING:
    raise ValueError("QUEUE_NAME and AZURITE_CONNECTION_STRING must be set")

# prepare services.
llm_service = LLMClassifierService()
geo_service = GeoService()

# init.
queue_client = get_queue_client()
ensure_queue(queue_client)
process_messages(queue_client, llm_service, geo_service)
