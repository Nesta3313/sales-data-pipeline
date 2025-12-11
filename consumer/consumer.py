import os
from kafka import KafkaConsumer
import json
import pandas as pd
from datetime import datetime


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "orders")

S3_BUCKET = os.getenv("S3_BUCKET", "orders-lake")
S3_PREFIX = os.getenv("S3_PREFIX", "raw/orders")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://minio:9000")



def main():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="orders-consumer-group",
    )

    buffer = []
    batch_size = 100

    for msg in consumer:
        event = msg.value
        buffer.append(event)

        if len(buffer) >= batch_size:
            df = pd.DataFrame(buffer)
            buffer.clear()

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            key = f'{S3_PREFIX}/orders_{ts}.parquet'
            s3_path = f"s3://{S3_BUCKET}/{key}"

            df.to_parquet(s3_path,
                          storage_options={
                              "key": os.getenv("AWS_ACCESS_KEY_ID"),
                              "secret": os.getenv("AWS_SECRET_ACCESS_KEY"),
                              "client_kwargs": {
                                  "endpoint_url": S3_ENDPOINT_URL
                              },
                          },
                          index=False)
            print(f'Wrote batch to {s3_path}')





if __name__ == '__main__':
    main()
