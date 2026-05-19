import os
import time
from azure.storage.queue import QueueServiceClient

QUEUE_NAME = "ticket-llm-classification-queue"
CONNECTION_STRING = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING",
    "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;QueueEndpoint=http://azurite:10001/devstoreaccount1;"
)


def main():
    service = QueueServiceClient.from_connection_string(CONNECTION_STRING)

    try:
        service.create_queue(QUEUE_NAME)
        print(f"Queue '{QUEUE_NAME}' created")
    except Exception:
        print(f"Queue '{QUEUE_NAME}' already exists")

    queue_client = service.get_queue_client(QUEUE_NAME)
    print(f"Listening for messages on '{QUEUE_NAME}'...")

    while True:
        messages = queue_client.receive_messages(messages_per_page=1, visibility_timeout=30)
        for msg in messages:
            print("hello world")
            queue_client.delete_message(msg)
        time.sleep(2)


if __name__ == "__main__":
    main()
