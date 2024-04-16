FROM python:3.9-slim
# todo python:3.12-slim
WORKDIR /app

COPY src/requirements.txt .
RUN pip install -r requirements.txt # --no-cache-dir

COPY src/ /app/src/

CMD ["python", "src/main.py"]
