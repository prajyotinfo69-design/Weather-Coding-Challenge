from sqlalchemy import Column, Integer, String, Date, Float, UniqueConstraint
from src.db.base import Base

class Weather(Base):
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String(16), nullable=False)
    date = Column(Date, nullable=False)
    max_temp_c = Column(Float)
    min_temp_c = Column(Float)
    precip_mm = Column(Float)

    __table_args__ = (UniqueConstraint("station_id", "date", name="uix_station_date"),)
