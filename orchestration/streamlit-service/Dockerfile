FROM python:3.12-slim

WORKDIR /app

COPY streamlit-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY streamlit-service/*.py .
COPY streamlit-service/pages/ pages/
COPY data/ data/

CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5682", "-m", "streamlit", "run", "main.py", "--server.port=5683", "--server.address=0.0.0.0"]
