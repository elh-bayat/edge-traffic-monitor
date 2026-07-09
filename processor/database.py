from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import String, Float, Integer, DateTime
from datetime import datetime


class Base(DeclarativeBase):
    pass


class TrafficReading(Base):
    __tablename__ = "traffic_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    camera_id: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    vehicle_count: Mapped[int] = mapped_column(Integer, nullable=False)
    average_speed_kmh: Mapped[float] = mapped_column(Float, nullable=False)
    weather: Mapped[str] = mapped_column(String(50), nullable=False)
    congestion_score: Mapped[float] = mapped_column(Float, nullable=False)


def get_engine(database_url: str):
    url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    return create_async_engine(url, echo=False)


def get_session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False)
