FROM python:3.11-slim

WORKDIR /app

COPY consumer.py .

RUN pip install --no-cache-dir \
    kafka-python \
    pandas \
    pyarrow \
    s3fs

CMD ["python", "consumer.py"]
