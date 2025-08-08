from datetime import date
from typing import Optional
from pydantic import BaseModel

class WeatherOut(BaseModel):
    station_id: str
    date: date
    max_temp_c: Optional[float]
    min_temp_c: Optional[float]
    precip_mm: Optional[float]

    class Config:
        from_attributes = True


class WeatherStatOut(BaseModel):
    station_id: str
    year: int
    avg_max_temp_c: Optional[float]
    avg_min_temp_c: Optional[float]
    total_precip_cm: Optional[float]

    class Config:
        from_attributes = True
