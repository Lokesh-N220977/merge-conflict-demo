import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")


async def seed_leaves():
    client = AsyncIOMotorClient(MONGO_URL, tlsAllowInvalidCertificates=True)
    db = client.health_appointment

    # 1. Clear existing leaves if any
    await db.leaves.drop()

    # 2. Fetch doctors to get their IDs
    doctors = await db.doctors.find().to_list(length=100)
    if not doctors:
        print("No doctors found to seed leaves for.")
        client.close()
        return

    leaves = []
    today = datetime.now()

    # Seed a few leaves for testing
    # Doctor 1: Leave in 3 days
    leaves.append({
        "doctor_id": str(doctors[0]["_id"]),
        "leave_date": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
        "reason": "Personal Leave"
    })

    # Doctor 2: Leave in 5 and 6 days
    leaves.append({
        "doctor_id": str(doctors[1]["_id"]),
        "leave_date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
        "reason": "Medical Conference"
    })
    leaves.append({
        "doctor_id": str(doctors[1]["_id"]),
        "leave_date": (today + timedelta(days=6)).strftime("%Y-%m-%d"),
        "reason": "Medical Conference"
    })

    # Doctor 3: Leave in 10 days
    leaves.append({
        "doctor_id": str(doctors[2]["_id"]),
        "leave_date": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
        "reason": "Vacation"
    })

    if leaves:
        await db.leaves.insert_many(leaves)
        print(f"✅ Seeded {len(leaves)} leaves for doctors.")

    client.close()

if __name__ == "__main__":
    asyncio.run(seed_leaves())
