from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.models.weather import Weather
from src.schemas.weather import WeatherOut

router = APIRouter()

def _paginate(q, page: int, size: int):
    return q.limit(size).offset((page - 1) * size)

@router.get("/weather", response_model=List[WeatherOut])
def read_weather(
    station_id: Optional[str] = Query(None),
    filter_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(Weather)
    if station_id:
        q = q.filter(Weather.station_id == station_id)
    if filter_date:
        q = q.filter(Weather.date == filter_date)
    q = q.order_by(Weather.date)
    return _paginate(q, page, page_size).all()
