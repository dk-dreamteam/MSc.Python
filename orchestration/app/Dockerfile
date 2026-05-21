FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ api/
COPY main.py .

CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5000", "main.py"]
