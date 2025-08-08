# Weather & Yield Data API

This project provides a FastAPI-based web API for managing and querying daily weather observations and yearly climate statistics for US midwest stations. The system incorporates ingestion routines for loading raw weather files, recomputes yearly statistics, and provides an REST API for data access.

- Python 3.12 
- FastAPI
- PostgreSQL 17
- SQLAlchemy 
- Typer CLI for data ingestion command
- Docker + Compose 

---

## Project layout

```
weather-code/                  
├── src/                      
│   ├── __init__.py
│   ├── main.py                # FastAPI entry‑point
│   ├── core/                  # settings
│   ├── db/                    # engine & session helpers
│   ├── models/                # Weather, WeatherStat, YieldData
│   ├── schemas/               # Pydantic response
│   ├── api/                   # route modules
│   └── services/              # ingestion + aggregation logic
├── scripts/
│   └── manage.py              # Typer CLI (ingest‑weather / ingest‑yield / stats / init‑db)
├── wx_data/                   # raw station txt files 
├── yld_data/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── tests/                     # pytest suite
```

---

## Quick start (Docker Compose)

```bash
# 1. Build images & start services (db + API)
docker compose up -d --build

# 2. Ingest raw weather observations
docker compose exec app \
  python scripts/manage.py ingest-weather /weather_code/wx_data

# 3. Ingest yearly crop yield
docker compose exec app \
  python scripts/manage.py ingest-yield /weather_code/yld_data/US_corn_grain_yield.txt

# 4. Compute / refresh yearly station statistics
docker compose exec app \
  python scripts/manage.py stats
```


Open Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Local (virtual‑env) workflow

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Replace database_username, database_password, database_name with actual values
export DATABASE_URL=postgresql+psycopg2://{database_username}:{database_password}@localhost:5432/{database_name}

# Initialize database
python scripts/manage.py init-db

# Load data
python scripts/manage.py ingest-weather ./wx_data
python scripts/manage.py ingest-yield ./yld_data/US_corn_grain_yield.txt
python scripts/manage.py stats

# Run API with reload
uvicorn src.main:app --reload
```
### Note: 
In case its throwing import errors, run the following command on same shell on which to execute below commands
```bash
  export PYTHONPATH=.
```

---

## Testing

```bash
pytest 
```

All tests use SQLite in‑memory.

---

## Environment variables

| Variable            | Default (inside container)                                          | Purpose                   |
| ------------------- | ------------------------------------------------------------------- | ------------------------- |
| `DATABASE_URL`      | `postgresql+psycopg2://weather_user:weather_pass@db:5432/weatherdb` | SQLAlchemy connection URL |
| `PAGE_SIZE_DEFAULT` | `50`                                                                | Default pagination size   |
| `PAGE_SIZE_MAX`     | `500`                                                               | Max page size             |

Override them in `docker-compose.yml`.

---

## API Reference

### GET /api/weather

Return daily weather observations.

**Query Parameters:**

- `station_id` (string, optional): filter by station
- `filter_date` (date, optional):filter by date (`YYYY-MM-DD`)
- `page` (int, default 1): page number
- `page_size` (int, default 50, max 500): items per page

**Response**: List of [WeatherOut](#weatherout) objects.

![api-weather.png](images/api-weather.png)
---

### GET /api/weather/stats

Return yearly weather statistics per station.

**Query Parameters:**

- `station_id` (string, optional): filter by station
- `year` (int, optional): filter by year
- `page` (int, default 1): page number
- `page_size` (int, default 50, max 500): items per page

**Response**: List of [WeatherStatOut](#weatherstatout) objects.

![api-weather-stats.png](images/api-weather-stats.png)
---

## Command Line Interface

The script can be invoked with several subcommands:

- `ingest-weather <path>`: Load all weather data from the specified directory.
- `init-db`: Initializes database.
- `stats`: Recompute the annual statistics table.


## Schema

### WeatherOut

```code
{
"station_id": "string",
"date": "YYYY-MM-DD",
"max_temp_c": float|null,
"min_temp_c": float|null,
"precip_mm": float|null
}
```

### WeatherStatOut

```code
{
"station_id": "string",
"year": int,
"avg_max_temp_c": float|null,
"avg_min_temp_c": float|null,
"total_precip_cm": float|null
}
```

---

## Helper Functions

- **init_db**: Create database tables if they do not exist.
- **get_db**: Dependency for FastAPI routes to provide a database session.
- **\_paginate**: Helper for paginating queries.

---

## Notes

- Database constraints ensure idempotent ingestion and prevent duplication.
- All endpoints support pagination for large datasets.
- All date and unit conversions are handled automatically during ingestion.

## Deployment
See [AWSSOlution.md](AWSSOlution.md)

