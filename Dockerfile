FROM apache/airflow:2.9.3-python3.12

USER root
RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER airflow
RUN pip install --no-cache-dir \
    pandas \
    s3fs \
    psycopg2-binary
