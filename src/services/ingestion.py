import os
from datetime import datetime
import logging
from sqlalchemy.dialects.postgresql import insert as pg_insert
from src.db.session import SessionLocal
from src.models.weather import Weather
from src.models.yield_data import YieldData


logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

def _parse_int_or_none(raw: str) -> float | None:
    v = int(raw)
    return None if v == -9999 else round(v, 1)

def _flush(buf, db):
    if not buf:
        return
    stmt = pg_insert(Weather).values(buf).on_conflict_do_nothing()
    db.execute(stmt)
    db.commit()
    buf.clear()

def ingest_weather_dir(path: str, batch_size: int = 10_000):
    db = SessionLocal()
    buf = []
    t0 = datetime.now()
    logger.info("Ingestion started: %s", path)
    for fname in os.listdir(path):
        if not fname.endswith(".txt"):
            continue
        station = fname.split(".")[0]
        with open(os.path.join(path, fname)) as fh:
            for line in fh:
                ds, tmax, tmin, prcp = line.strip().split("\t")
                buf.append(
                    dict(
                        station_id=station,
                        date=datetime.strptime(ds, "%Y%m%d").date(),
                        max_temp_c=_parse_int_or_none(tmax),
                        min_temp_c=_parse_int_or_none(tmin),
                        precip_mm=_parse_int_or_none(prcp),
                    )
                )
                if len(buf) >= batch_size:
                    _flush(buf, db)
        logger.info(f"loaded {fname}")
    _flush(buf, db)
    db.close()
    logger.info(f"Ingestion Finished {(datetime.now() - t0).total_seconds()}")

def ingest_yield_file(file_path: str):
    db = SessionLocal()
    rows = []
    with open(file_path) as fh:
        for line in fh:
            if line.strip():
                yr, val = line.split()
                rows.append({"year": int(yr), "total_yield": int(val)})
    stmt = pg_insert(YieldData).values(rows).on_conflict_do_nothing()
    db.execute(stmt)
    db.commit()
    db.close()
