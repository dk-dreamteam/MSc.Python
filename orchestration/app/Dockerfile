FROM python:3.12-slim
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/app.py .
COPY common_services/ common_services/
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
