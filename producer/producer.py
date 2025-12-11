import uuid
import random
import json
from datetime import datetime, timezone
import time
import os

from kafka import KafkaProducer

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "orders")

CATEGORIES = ["electronics", "fashion", "groceries", "books", "gaming"]
COUNTRIES = ["US", "GB", "NG", "DE", "IN", "ZA"]
CURRENCIES = ["USD", "EUR", "NGN", "GBP"]

def generate_order_event():
    return {
        'order_id': str(uuid.uuid4()),
        'user_id': str(uuid.uuid4()),
        'amount': round(random.uniform(50, 500), 2),
        'currency': random.choice(CURRENCIES),
        'category': random.choice(CATEGORIES),
        'country': random.choice(COUNTRIES),
        'created_at': datetime.now(timezone.utc).isoformat()

    }


def main():
    producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    while True:
        event = generate_order_event()
        producer.send(KAFKA_TOPIC, value=event)
        print('Sent', event)
        time.sleep(0.5)

if __name__ == '__main__':
    main()
