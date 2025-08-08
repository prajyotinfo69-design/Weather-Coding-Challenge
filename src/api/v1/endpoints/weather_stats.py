from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.models.weather_stat import WeatherStat
from src.schemas.weather import WeatherStatOut

router = APIRouter()

def _paginate(q, page: int, size: int):
    return q.limit(size).offset((page - 1) * size)

@router.get("/weather/stats", response_model=List[WeatherStatOut])
def read_weather_stats(
    station_id: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(WeatherStat)
    if station_id:
        q = q.filter(WeatherStat.station_id == station_id)
    if year:
        q = q.filter(WeatherStat.year == year)
    q = q.order_by(WeatherStat.year)
    return _paginate(q, page, page_size).all()
