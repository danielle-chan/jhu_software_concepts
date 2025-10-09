Danielle Chan - JHID: F84B10
Module 6
Due Date: 10/09/2025 4:30PM

Overview:
This module extends the GradCafe ETL + Web Application into a fully containerized, asynchronous data pipeline using Docker Compose and RabbitMQ.
The architecture separates the system into independent services for web, worker, database, and message broker, enabling parallel and decoupled processing.

New Components Introduced
* Dockerized Services - web, worker, db, rabbitmq managed via docker-compose.yml.
* Publisher / Consumer Messaging – Flask endpoints now publish tasks (scrape_new_data, recompute_analytics) to RabbitMQ queues.
* Worker Automation – Background consumer listens for messages, triggers incremental scrapes, and recomputes analytics.
* Persistent Watermarks Table – Implements idempotent inserts with ingestion_watermarks to avoid duplicate records.
* Materialized View Refresh – Adds handle_recompute_analytics to update applicant_summary.
* Async Front-End Buttons – Flask UI uses JS fetch() to queue background tasks and show status banners.
* Docker Hub Integration – Container images built and pushed to daniellechan/module_6.

The enhanced system now follows this flow:
1. Scrape - GradCafe incremental posts
2. Publish - RabbitMQ task message
3. Consume & Load - Worker processes data into PostgreSQL
4. Analyze & Display - Flask queries and renders summary statistics

Requirements
* Docker Desktop ( with Docker CLI )
* Docker Compose v2 or later
* Python 3.11 (inside containers)

All Python dependencies are installed via each image’s requirements.txt:
Flask>=2.3
psycopg[binary]>=3.1
pika>=1.3
beautifulsoup4>=4.12
pytest
pytest-cov

Setup and Running the Application
1. Build and Launch Containers
docker compose up --build

This starts four services:
* web - Flask app ( localhost:8080 )
* worker - RabbitMQ consumer for ETL tasks
* db - PostgreSQL database ( localhost:5432 )
* rabbitmq - Message broker ( localhost:15672 UI: guest/guest )

2. Verify Database Schema
docker compose exec -T db psql -U postgres -d applicants -c "\dt"
Tables should include applicants, applicant_summary, and ingestion_watermarks.

3. Trigger Async Tasks
Open http://localhost:8080
Click Pull Data or Update Analysis.
A green banner appears indicating the task was queued.

4. Monitor Worker Logs
docker compose logs -f worker

5. Inspect Results
docker compose exec -T db psql -U postgres -d applicants -c "SELECT COUNT(*) FROM applicants;"
docker compose exec -T db psql -U postgres -d applicants -c "SELECT * FROM ingestion_watermarks;"

File Structure:
module_6/
│
├── docker-compose.yml
│
├── web/
│   ├── Dockerfile
│   ├── run.py                # Flask app + RabbitMQ publishers
│   ├── publisher.py          # Publishes task messages
│   ├── templates/index.html  # Async UI buttons & stats
│   └── requirements.txt
│
├── worker/
│   ├── Dockerfile
│   ├── consumer.py           # RabbitMQ consumer with DB transactions
│   ├── etl/
│   │   ├── incremental_scraper.py
│   │   ├── append_data.py
│   │   ├── query_data.py
│   │   ├── sql_helpers.py
│   │   └── __init__.py
│   └── db/
│       ├── init.sql
│       └── load_data.py
│
└── data/
    └── full_out.jsonl

Testing and Validation:
* Verified message flow: Flask → RabbitMQ → Worker → PostgreSQL
* Confirmed idempotent inserts via ingestion_watermarks updates.
* Verified applicant_summary refresh via handle_recompute_analytics.
* Docker images successfully built and pushed:
    * daniellechan/module_6-web:v1
    * daniellechan/module_6-worker:v1

Issues Encountered & Resolutions
* RabbitMQ connection errors – Resolved by ensuring RABBITMQ_URL matches container network.
* Duplicate inserts – Prevented via ON CONFLICT and ingestion_watermarks.
* Broken Dockerfile CMD – Fixed to use JSON array syntax ["python","run.py"].
* Missing volume conflicts – Removed duplicate volumes: keys in docker-compose.yml.
* Table not found errors – Ensured init.sql creates required schema before worker starts.
* Front-end layout bug – Adjusted index.html to stack analysis sections vertically.

Outcome:
By completing Module 6, the GradCafe pipeline is now a robust, containerized, event-driven system.
It demonstrates end-to-end mastery of data engineering, asynchronous processing, and cloud-native architecture principles using modern Python tools.
