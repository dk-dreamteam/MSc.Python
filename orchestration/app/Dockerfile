FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/api/ api/
COPY app/main.py .
COPY internal-services/photo_blob_service/ photo_blob_service/
COPY internal-services/queue_sender_service/ queue_sender_service/
COPY data/ data/

CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5681", "main.py"]
