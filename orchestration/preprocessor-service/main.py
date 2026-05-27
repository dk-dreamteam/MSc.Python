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
            try:
                # json deserialize and get ticket id to work on.
                data = json.loads(message.content)
                id = data.get("id")

                # job1: Fetch ticket from database by id.
                ticket = repo.get_ticket(id)

                # job2: Communicate with LLM to get the description classification.
                category_id = llm_service.Classify(ticket.description)

                # job3: Communicate with LLM to get the priority.
                priority = llm_service.ClassifyPriority(ticket.description)

                # job4: Communicate with OpenStreetMap nominatim to get the lat long from the address.
                lat, lon = geo_service.GetCoordinatesFromAddress(ticket.address)

                # job4: Update the ticket in the database with updated values.
                repo.update_ticket(str(ticket.id), {"category_id": category_id, "ai_priority_suggestion":priority, "latitude": lat, "longitude": lon})
                logger.info("Processed: category=%d, lat=%f, lon=%f", category_id, lat, lon)
            except Exception as e:
                logger.error("Failed to process message: %s", e)
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
