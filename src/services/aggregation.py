
from sqlalchemy import func, delete, inspect

from src.models.weather import Weather
from src.models.weather_stat import WeatherStat
from src.db.session import engine

def recompute_stats(db=None):
    owns_session = False
    if db is None:
        from src.db.session import SessionLocal
        db = SessionLocal()
        owns_session = True

    if not inspect(engine).has_table(WeatherStat.__tablename__):
        WeatherStat.__table__.create(bind=engine)
    else:
        db.execute(delete(WeatherStat))
    rows = (
        db.query(
            Weather.station_id.label("station"),
            func.extract("year", Weather.date).label("yr"),
            func.avg(Weather.max_temp_c).label("avg_max"),
            func.avg(Weather.min_temp_c).label("avg_min"),
            (func.sum(Weather.precip_mm) / 10.0).label("total_cm"),
        )
        .group_by(Weather.station_id, func.extract("year", Weather.date))
        .all()
    )

    for r in rows:
        db.add(
            WeatherStat(
                station_id=r.station,
                year=int(r.yr),
                avg_max_temp_c=round(r.avg_max, 2) if r.avg_max else r.avg_max,
                avg_min_temp_c=round(r.avg_min, 2) if r.avg_min else r.avg_min,
                total_precip_cm=round(r.total_cm, 2) if r.total_cm else r.total_cm,
            )
        )

    db.commit()
    if owns_session:
        db.close()
