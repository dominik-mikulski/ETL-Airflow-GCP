# Extract Transform Load pipeline with Airflow

**Project Summary:**
Hands-on Apache Airflow 3.1+ ETL pipeline that fetches live weather data, transforms it, and loads it into PostgreSQL. Fully containerized with Docker, uses CeleryExecutor + Redis for scalable task orchestration, and demonstrates a realistic Airflow pipeline.

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Airflow](https://img.shields.io/badge/Apache%20Airflow-3.1+-orange)](https://airflow.apache.org/)
[![Docker](https://img.shields.io/badge/Docker-24-blue)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7.2-red)](https://redis.io/)

---

## What I Learned / Key Takeaways

- Designing and implementing **Airflow DAGs**
- Using **CeleryExecutor + Redis** for scalable task orchestration
- Managing **PostgreSQL connections** and safe data inserts with Python
- Handling **XComs properly**, avoiding serialization issues
- Containerized development with **Docker Compose** for Airflow services
- Debugging DAGs and tasks

---

## Architecture

This setup mirrors **production-like deployments (2025 standards):**

| Component        | Technology / Version            | Notes |
|-----------------|---------------------------------|-------|
| Executor        | CeleryExecutor                  | Scalable, battle-tested |
| Task Queue      | Redis                           | Fast, in-memory broker |
| Metadata DB     | PostgreSQL 16                   | Dedicated volume, isolated |
| Web UI / API    | Airflow FastAPI apiserver (8080)| Modern, responsive |

---

## Features

- Fully containerized with **official Apache Airflow 3.1+ Docker images**
- Uses **CeleryExecutor + Redis** for real-world task orchestration
- Isolated PostgreSQL volume – safe to run alongside other instances
- Modern Airflow UI with FastAPI apiserver
- Ready to run with any public API – just drop DAGs into `dags/`
- **Zero extra Python dependencies** beyond the official Airflow image
- Example ETL DAG included: fetches live weather data and stores it in PostgreSQL

---

## Quickstart (Docker – Windows/macOS/Linux)

```bash
# 1. Clone the repository
git clone https://github.com/dominik-mikulski/Airflow.git
cd Airflow

# 2. Add your API key to dags/etl.py
Open https://openweathermap.org/, setup account, copy API key. Open dags/etl.py and follow steps. 

# 3. Create the .env file with correct user ID
# Windows PowerShell:
'AIRFLOW_UID=50000' | Set-Content -Path .env -Encoding UTF8NoBOM

# macOS / Linux / WSL:
echo "AIRFLOW_UID=$(id -u)" > .env

# 4. Initialize Airflow DB (first time only)
docker compose up airflow-init

# 5. Start Airflow services in background
docker compose up -d

# 6. Access the UIs
Airflow:   http://localhost:8080   (login: airflow / airflow)
Adminer:   http://localhost:8081   (System: PostgreSQL, Server: postgres:5432, login: airflow / airflow)

# 7. Stop everything and clean up
docker compose down -v
```

---

## Project Structure

```
├── dags/            ← Put your DAGs here
├── data/            ← Example output directory (gitignored)
├── logs/            ← Airflow logs (gitignored)
├── docker-compose.yaml
└── README.md
```

## Future Improvements
- Add **logging** and better **error handling**
- Include **unit and integration tests**
- Implement **graceful task failure recovery**
- Enhance **security and network separation**
- Currently **not production-ready**; this is a showcase and learning project.

