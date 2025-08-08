from sqlalchemy import Column, Integer
from src.db.base import Base

class YieldData(Base):
    __tablename__ = "yield"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, unique=True)
    total_yield = Column(Integer, nullable=False)
