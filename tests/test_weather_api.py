from datetime import date
from typing import Generator

import pytest
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.base import Base
from src.models.weather import  Weather
from src.models.weather_stat import WeatherStat
from src.services.aggregation import recompute_stats


@pytest.fixture(scope="session")
def engine() -> Generator:
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()

@pytest.fixture()
def db_session(engine):
    connection = engine.connect()
    txn = connection.begin()       # everything inside this txn
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    txn.rollback()
    connection.close()



@pytest.fixture()
def client(db_session):

    from src.main import app
    from src.api.deps import get_db

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def _seed_raw_weather(db):
    """Insert a dummy set of Weather rows."""
    db.add_all(
        [
            Weather(
                station_id="TEST1",
                date=date(2000, 1, 1),
                max_temp_c=10.0,
                min_temp_c=0.0,
                precip_mm=1.0,
            ),
            Weather(
                station_id="TEST1",
                date=date(2000, 1, 2),
                max_temp_c=20.0,
                min_temp_c=5.0,
                precip_mm=2.0,
            ),
            # Second station, ensure filters work
            Weather(
                station_id="TEST2",
                date=date(2001, 6, 1),
                max_temp_c=30.0,
                min_temp_c=15.0,
                precip_mm=0.0,
            ),
        ]
    )
    db.commit()


# def test_recompute_stats(db_session):
#
#     _seed_raw_weather(db_session)
#     recompute_stats(db_session)
#
#     stats = db_session.query(WeatherStat).all()
#     assert len(stats) == 2  # TEST1‑2000 and TEST2‑2001
#
#     s1 = next(s for s in stats if s.station_id == "TEST1")
#     assert s1.year == 2000
#     assert s1.avg_max_temp_c == pytest.approx((10.0 + 20.0) / 2)
#     assert s1.total_precip_cm == pytest.approx((1.0 + 2.0) / 10.0)  # mm → cm
#
#
# def test_api_weather_endpoint(client, db_session):
#     _seed_raw_weather(db_session)
#
#     resp = client.get("/api/weather?page_size=10")
#     assert resp.status_code == 200
#     data = resp.json()
#     assert len(data) == 3
#
#     # Filter by station
#     resp = client.get("/api/weather", params={"station_id": "TEST1"})
#     assert resp.status_code == 200
#     assert len(resp.json()) == 2
#
#     # Date range filter
#     resp = client.get(
#         "/api/weather",
#         params={
#             "filter_date": "2000-01-02",
#         },
#     )
#     assert len(resp.json()) == 1
#
#
# def test_api_stats_endpoint(client, db_session):
#
#     _seed_raw_weather(db_session)
#     recompute_stats(db_session)
#
#     resp = client.get("/api/weather/stats")
#     assert resp.status_code == 200
#     stats = resp.json()
#     assert len(stats) == 2
#
#     # Filter by station & year
#     resp = client.get("/api/weather/stats", params={"station_id": "TEST2", "year": 2001})
#     assert resp.status_code == 200
#     filtered = resp.json()
#     assert len(filtered) == 1
#     assert filtered[0]["station_id"] == "TEST2"

# ── recompute_stats tests ──────────────────────────────────────────────────────
def test_stats_count(db_session):
    _seed_raw_weather(db_session)
    recompute_stats(db_session)

    stats = db_session.query(WeatherStat).all()
    assert len(stats) == 2


def test_stats_values_station1(db_session):
    _seed_raw_weather(db_session)
    recompute_stats(db_session)

    s1 = (
        db_session.query(WeatherStat)
        .filter_by(station_id="TEST1", year=2000)
        .one()
    )
    assert s1.avg_max_temp_c == pytest.approx((10.0 + 20.0) / 2)
    assert s1.total_precip_cm == pytest.approx((1.0 + 2.0) / 10.0)  # mm → cm


# ── /api/weather endpoint tests ────────────────────────────────────────────────
def test_weather_list_all(db_session, client):
    _seed_raw_weather(db_session)

    resp = client.get("/api/weather?page_size=10")
    assert resp.status_code == 200
    assert len(resp.json()) == 3


def test_weather_filter_by_station(db_session, client):
    _seed_raw_weather(db_session)

    resp = client.get("/api/weather", params={"station_id": "TEST1"})
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_weather_filter_by_date_range(db_session, client):
    _seed_raw_weather(db_session)

    resp = client.get(
        "/api/weather",
        params={"filter_date": "2000-01-02"},
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1


# ── /api/weather/stats endpoint tests ──────────────────────────────────────────
def test_stats_list_all(db_session, client):
    _seed_raw_weather(db_session)
    recompute_stats(db_session)

    resp = client.get("/api/weather/stats")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_stats_filter_station_year(db_session, client):
    _seed_raw_weather(db_session)
    recompute_stats(db_session)

    resp = client.get(
        "/api/weather/stats", params={"station_id": "TEST2", "year": 2001}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["station_id"] == "TEST2"
