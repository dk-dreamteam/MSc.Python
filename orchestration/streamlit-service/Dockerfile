FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .
COPY pages/ pages/

CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5682", "-m", "streamlit", "run", "main.py", "--server.port=5683", "--server.address=0.0.0.0"]
