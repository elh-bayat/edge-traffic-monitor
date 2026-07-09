import asyncio
import json
import os
import logging
from datetime import datetime
import aio_pika
from dotenv import load_dotenv
from prometheus_client import Counter, start_http_server
from database import Base, TrafficReading, get_engine, get_session_factory

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://admin:admin123@localhost:5672/")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://traffic_user:traffic_pass@localhost:5432/traffic_db")
QUEUE_NAME = "traffic_readings"

messages_processed = Counter("processor_messages_total", "Total messages processed")


def compute_congestion_score(vehicle_count: int, speed: float) -> float:
    speed_factor = max(0.0, 1.0 - (speed / 120.0))
    count_factor = min(1.0, vehicle_count / 80.0)
    return round(speed_factor * 0.6 + count_factor * 0.4, 3)


async def process_message(message: aio_pika.IncomingMessage, Session):
    async with message.process():
        data = json.loads(message.body.decode())
        score = compute_congestion_score(data["vehicle_count"], data["average_speed_kmh"])
        reading = TrafficReading(
            camera_id=data["camera_id"],
            location=data["location"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            vehicle_count=data["vehicle_count"],
            average_speed_kmh=data["average_speed_kmh"],
            weather=data["weather"],
            congestion_score=score,
        )
        async with Session() as session:
            session.add(reading)
            await session.commit()
        messages_processed.inc()
        logger.info(f"Saved {data['camera_id']} | vehicles={data['vehicle_count']} | congestion={score}")


async def main():
    start_http_server(8001)
    logger.info("Prometheus metrics on :8001")

    engine = get_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ready")
    Session = get_session_factory(engine)

    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)

    async def on_message(message):
        await process_message(message, Session)

    await queue.consume(on_message)
    logger.info(f"Consuming from queue '{QUEUE_NAME}'...")
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
