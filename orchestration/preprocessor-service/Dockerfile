FROM python:3.12-slim

WORKDIR /app

COPY preprocessor-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY preprocessor-service/*.py .
COPY data/ data/
ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5679", "main.py"]
