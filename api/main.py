from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
import os, logging
import aio_pika
from dotenv import load_dotenv
from prometheus_fastapi_instrumentator import Instrumentator
from models import TrafficReading, TrafficReadingResponse

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Edge Traffic Monitor API", version="1.0.0")
Instrumentator().instrument(app).expose(app)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://admin:admin123@localhost:5672/")
QUEUE_NAME = "traffic_readings"
rabbitmq_channel = None


@app.on_event("startup")
async def startup():
    global rabbitmq_channel
    import aio_pika
    for attempt in range(10):  # Try up to 10 times
        try:
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            channel = await connection.channel()
            await channel.declare_queue(QUEUE_NAME, durable=True)
            rabbitmq_channel = channel
            logger.info("Connected to RabbitMQ")
            return
        except Exception as e:
            logger.warning(f"RabbitMQ not ready (attempt {attempt+1}/10): {e}")
            await asyncio.sleep(5)
    logger.error("Could not connect to RabbitMQ after 10 attempts")


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/api/v1/traffic", response_model=TrafficReadingResponse, status_code=201)
async def receive_traffic(reading: TrafficReading):
    if rabbitmq_channel is None:
        raise HTTPException(status_code=503, detail="Message broker not available")

    message_body = reading.model_dump_json().encode()
    await rabbitmq_channel.default_exchange.publish(
        aio_pika.Message(body=message_body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
        routing_key=QUEUE_NAME,
    )
    logger.info(f"Queued reading from {reading.camera_id}")

    return TrafficReadingResponse(
        message="Reading accepted",
        camera_id=reading.camera_id,
        received_at=datetime.now(timezone.utc),
    )
