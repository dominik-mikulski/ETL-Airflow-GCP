# ETL (Extract Transform Load) – Airflow Showcase Project

Simple, Airflow project that demonstrates a complete ETL pipeline using the official Apache Airflow 3.1+ Docker setup.

Perfect as a portfolio piece or interview take-home task.

### Architecture (exactly like most production deployments in 2025)
- Executor:      CeleryExecutor (scalable, battle-tested)
- Task queue:    Redis (in-memory, extremely fast)
- Metadata DB:   PostgreSQL 16
- UI:            Modern FastAPI apiserver (port 8080)

## Features
- Latest Airflow 3.1+ with modern FastAPI UI (apiserver on port 8080)
- Fully containerised with official `apache/airflow` images
- Dedicated PostgreSQL volume – does NOT interfere with any other Airflow/Postgres instances you have
- No extra Python dependencies – everything is provided by the official image
- Ready for any public API → just drop your DAG into `dags/`

## Quickstart (Docker – recommended, works on Windows/macOS/Linux)

```bash
# 1. Clone the repo
git clone https://github.com/dominik-mikulski/Airflow.git
cd Airflow

# 2. Create the required .env file
# Windows PowerShell:
'AIRFLOW_UID=50000' | Set-Content -Path .env -Encoding UTF8NoBOM

# macOS / Linux / WSL:
echo "AIRFLOW_UID=$(id -u)" > .env

# 3. Initialize the database (only needed the first time)
docker compose up airflow-init

# 4. Start Airflow in background
docker compose up -d

# 5. Access UIs
AIRFLOW: http://localhost:8080 # login: airflow / airflow
ADMINER: http://localhost:8081 # change sytem to PostgreSQL, Server: postgres:5432, login: ariflow\airflow

# 6. STOP EVERYTHING
docker compose down -v # this removes the container and one dedicate volume in it.

├── dags/            ← put your DAGs here
├── data/            ← example output directory (gitignored)
├── logs/            ← Airflow logs (gitignored)
├── docker-compose.yaml
└── README.md

