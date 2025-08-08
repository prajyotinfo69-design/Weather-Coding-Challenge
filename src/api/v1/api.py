from fastapi import APIRouter
from src.api.v1.endpoints import weather, weather_stats

api_router = APIRouter()
api_router.include_router(weather.router, prefix="/api", tags=["weather"])
api_router.include_router(weather_stats.router, prefix="/api", tags=["weather-stats"])
