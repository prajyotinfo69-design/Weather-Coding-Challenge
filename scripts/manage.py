import typer
from src.services.aggregation import recompute_stats
from src.services.ingestion import ingest_weather_dir, ingest_yield_file
from src.models import Base
from src.db.session import engine

cli = typer.Typer(add_completion=False)


@cli.command()
def init_db():
    """Create database schema (run once)."""
    Base.metadata.create_all(bind=engine)
    typer.echo("✓  Database schema created")

@cli.command()
def ingest_weather(path: str):
    """Bulk-load wx_data directory."""
    ingest_weather_dir(path)

@cli.command()
def ingest_yield(file: str):
    """Load yearly yield TSV file."""
    ingest_yield_file(file)

@cli.command()
def stats():
    """Recompute yearly station statistics."""
    recompute_stats()

if __name__ == "__main__":
    cli()
