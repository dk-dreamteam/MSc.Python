import os
import time
import json
import logging
from azure.storage.queue import QueueClient
from azure.core.exceptions import ResourceNotFoundError
from llm_classifier import LLMClassifierService
from geo_service import GeoService
from data.repository import TicketRepository

repo = TicketRepository()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

for _logger in ["azure", "azure.core", "azure.storage", "urllib3"]:
    logging.getLogger(_logger).setLevel(logging.WARNING)

QUEUE_NAME = os.getenv("PREPROCESSOR_QUEUE_NAME")
CONNECTION_STRING = os.getenv("AZURITE_QUEUE_CONNECTION_STRING")


def _get_queue_client() -> QueueClient:
    return QueueClient.from_connection_string(CONNECTION_STRING, QUEUE_NAME)


def _ensure_queue(queue_client):
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
            data = json.loads(message.content)
            id = data.get("id")

            # separating jobs with their own try catch to make sure that if one job fails, the rest of them may carry on.

            # Job 1: Category classification
            try:
                ticket = repo.get_ticket(id)
                category_id = llm_service.Classify(ticket.description)
                repo.update_ticket(str(ticket.id), {"category_id": category_id})
                logger.info("Category classified: %d", category_id)
            except Exception as e:
                logger.error("Category classification failed: %s", e)

            # Job 2: Priority classification
            try:
                ticket = repo.get_ticket(id)
                priority = llm_service.ClassifyPriority(ticket.description)
                repo.update_ticket(str(ticket.id), {"ai_priority_suggestion": priority})
                logger.info("Priority classified: %s", priority)
            except Exception as e:
                logger.error("Priority classification failed: %s", e)

            # Job 3: Geocoding
            try:
                ticket = repo.get_ticket(id)
                lat, lon = geo_service.GetCoordinatesFromAddress(ticket.address)
                repo.update_ticket(str(ticket.id), {"latitude": lat, "longitude": lon})
                logger.info("Geocoded: lat=%f, lon=%f", lat, lon)
            except Exception as e:
                logger.error("Geocoding failed: %s", e)

            queue_client.delete_message(message)
        time.sleep(1)


if not QUEUE_NAME or not CONNECTION_STRING:
    raise ValueError("PREPROCESSOR_QUEUE_NAME and AZURITE_QUEUE_CONNECTION_STRING must be set")

# prepare services.
llm_service = LLMClassifierService()
geo_service = GeoService()

# init.
queue_client = _get_queue_client()
_ensure_queue(queue_client)
process_messages(queue_client, llm_service, geo_service)
