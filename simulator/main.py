"""
Edge Device Simulator
Simulates 50 traffic cameras sending data to the API gateway.
"""

import asyncio
import random
import httpx
import os
from datetime import datetime, timezone

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/traffic")

LOCATIONS = [f"Street {chr(65 + i // 5)} - Intersection {(i % 5) + 1}" for i in range(50)]
WEATHERS = ["clear", "rain", "fog", "snow", "cloudy"]

NUM_CAMERAS = 50
SEND_INTERVAL_SECONDS = 5


def generate_payload(camera_id: int) -> dict:
    return {
        "camera_id": f"cam_{camera_id:02d}",
        "location": LOCATIONS[camera_id],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "vehicle_count": random.randint(0, 80),
        "average_speed_kmh": round(random.uniform(10.0, 120.0), 1),
        "weather": random.choice(WEATHERS),
    }


async def camera_loop(camera_id: int, client: httpx.AsyncClient):
    while True:
        payload = generate_payload(camera_id)
        try:
            response = await client.post(API_URL, json=payload, timeout=5.0)
            print(f"[cam_{camera_id:02d}] Sent → HTTP {response.status_code}")
        except httpx.ConnectError:
            print(f"[cam_{camera_id:02d}] API not reachable yet, retrying...")
        except Exception as e:
            print(f"[cam_{camera_id:02d}] Error: {e}")
        await asyncio.sleep(SEND_INTERVAL_SECONDS)


async def main():
    print(f"Starting {NUM_CAMERAS} camera simulators...")
    async with httpx.AsyncClient() as client:
        tasks = [camera_loop(i, client) for i in range(NUM_CAMERAS)]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
