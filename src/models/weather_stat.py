from sqlalchemy import Column, Integer, String, Float, UniqueConstraint
from src.db.base import Base

class WeatherStat(Base):
    __tablename__ = "weather_stats"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String(16), nullable=False)
    year = Column(Integer, nullable=False)

    avg_max_temp_c = Column(Float)
    avg_min_temp_c = Column(Float)
    total_precip_cm = Column(Float)

    __table_args__ = (UniqueConstraint("station_id", "year", name="uix_station_year"),)
