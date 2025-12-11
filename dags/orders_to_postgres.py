import json
import os
from datetime import timedelta, datetime

import pandas as pd
import s3fs
import sqlalchemy as sa
from airflow.models import Variable
from airflow import DAG
from airflow.operators.python import PythonOperator

S3_BUCKET = 'orders-lake'
S3_PREFIX = 'raw/orders'
S3_ENDPOINT_URL = 'http://minio:9000'


def load_new_batches_to_postgres(**context):
    fs = s3fs.S3FileSystem(
        key=os.getenv('AWS_ACCESS_KEY_ID'),
        secret=os.getenv('AWS_SECRET_ACCESS_KEY'),
        client_kwargs={'endpoint_url': S3_ENDPOINT_URL}
    )

    files = fs.glob(f'{S3_BUCKET}/{S3_PREFIX}/orders_*.parquet')

    if not files:
        print("No files found")
        return

    # Get previously processed files from Airflow Variable
    processed_raw_files = Variable.get('orders_processed_files', default_var='[]')
    processed_files = set(json.loads(processed_raw_files))

    new_files = [f for f in files if f not in processed_files]

    if not new_files:
        print('No new files to process')
        return

    for path in new_files:
        s3_path = f's3://{path}'
        print(f'Processing {s3_path}')

        df = pd.read_parquet(
            s3_path,
            storage_options={
                'key': os.getenv('AWS_ACCESS_KEY_ID'),
                'secret':  os.getenv('AWS_SECRET_ACCESS_KEY'),
                'client_kwargs':  {'endpoint_url': S3_ENDPOINT_URL},
            },
        )

        df['created_at'] = pd.to_datetime(df['created_at'])

        engine = sa.create_engine(
            "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow")

        df.to_sql(
            'fact_orders',
            engine,
            if_exists='append',
            index=False
        )

        print(f'Loaded {len(df)} rows from {s3_path} to fact_orders')

        # Mark this file as processed in our in-memory set
        processed_files.add(path)

    # Persist the updated list back into airflow variable
    Variable.set('orders_processed_files', json.dumps(list(processed_files)))
    print(f'Tracking {len(processed_files)} processed files')


default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

with DAG(
    dag_id='orders_minio_to_postgres',
    start_date=datetime(2024, 1, 1),
    schedule_interval='*/5 * * * *',
    catchup=False,
    default_args=default_args
) as dag:

    sync_orders = PythonOperator(
        task_id='sync_orders',
        python_callable=load_new_batches_to_postgres,
        provide_context=True
    )








