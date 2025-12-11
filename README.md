## Real-Time Streaming Architecture: Orders Pipeline

A compact data engineering project that simulates an end-to-end real-time order ingestion pipeline.
It streams synthetic e-commerce orders through **Kafka**, lands raw data into a **MinIO data lake**, and uses **Airflow** to orchestrate incremental batch loads into a **Postgres warehouse**.

This project demonstrates the classic ELT motion:

**Extract → Load → Transform (light transformations)**

---

## **Project Goals**

This project teaches the fundamentals of a modern streaming data pipeline:

* **Real-time event ingestion** using Kafka
* **Data lake storage** via S3-compatible MinIO
* **Workflow orchestration** with Airflow
* **Incremental batch loading** into a warehouse (Postgres)
* **Fully local infrastructure** via Docker Compose

---

## **1. Kafka Producer (Python)**

Continuously emits synthetic order events into the **orders** topic.

Each event contains:

* `order_id`, `user_id`
* `amount`, `currency`
* `category`, `country`
* `created_at`

This forms the pipeline’s **real-time ingestion layer**.

---

## **2. Kafka Consumer (Python)**

The counterpart listener that:

* Subscribes to the **orders** Kafka topic
* Buffers messages into batches (e.g., 100 rows)
* Converts batches into pandas DataFrames
* Writes each batch as a Parquet file into MinIO:

```
s3://orders-lake/raw/orders/orders_<timestamp>.parquet
```

---

## **3. MinIO (S3-Compatible Data Lake)**

A local object storage environment where all raw Parquet files land.

Directory structure:

```
orders-lake/
└── raw/orders/
      ├── orders_2025-12-11_00-00-01.parquet
      ├── orders_2025-12-11_00-00-06.parquet
      └── ...
```

MinIO holds **immutable raw data**, exactly as produced from Kafka.

---

## **4. Airflow 2.9.3 (LocalExecutor)**

Airflow orchestrates the **lake → warehouse** movement.

The DAG `orders_minio_to_postgres` runs every **5 minutes** and:

* Lists Parquet files in MinIO
* Retrieves previously processed files (via Airflow Variable)
* Processes only **new** files
* Loads curated batches into Postgres
* Updates the processed file tracking list

This acts as the pipeline’s **curation & loading layer**.

---

## **5. Postgres Warehouse**

A lightweight analytical warehouse storing curated facts.

### **fact_orders** table:

```sql
CREATE TABLE fact_orders (
  order_id    UUID PRIMARY KEY,
  user_id     UUID,
  amount      NUMERIC(10, 2),
  currency    VARCHAR(10),
  category    VARCHAR(50),
  country     VARCHAR(10),
  created_at  TIMESTAMP WITH TIME ZONE
);
```

Once loaded, data becomes query-ready for reporting and dashboards.

---

## **6. Optional BI Layer (Power BI / Metabase / Tableau)**

Hook Postgres into any BI tool to explore:

* Sales by country
* Sales by category
* Average order value
* Currency distributions
* Hourly/daily order trends

This turns the warehouse into a **living analytics hub**.

---

## **Dockerized Infrastructure**

Everything runs via:

```
docker compose up -d
```
```
cp airflow.env.example airflow.env
```

Then replace:

REPLACE_ME_FERNET_KEY
Generate one:

```
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
REPLACE_ME_SECRET_KEY
Generate:

```
openssl rand -hex 32
```

MinIO dev creds
(minioadmin, minioadmin123 for local testing)



Included services:

* **Kafka**
* **Zookeeper**
* **MinIO**
* **Postgres**
* **Airflow Webserver + Scheduler**

---

## **How Data Moves Through the System**

```
Python Producer → Kafka
Kafka Consumer → MinIO (raw parquet)
Airflow DAG → Postgres (curated facts)
Postgres → BI dashboards (insight layer)
```

---

## **Security Notes**

This repo uses **development-only credentials**:

* MinIO: `minioadmin / minioadmin123`
* Airflow: default admin user
* Fernet & secret keys: placeholders


