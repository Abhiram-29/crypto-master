# core/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect(cls):
        cls.client = AsyncIOMotorClient(
            settings.MONGO_URI, maxPoolSize=10, minPoolSize=1
        )
        cls.db = cls.client["CryptoMaster"]  # Replace with your database name

    @classmethod
    async def close(cls):
        if cls.client:
            cls.client.close()

async def get_database():  # Keep this for dependency injection
    if MongoDB.db is None:
        await MongoDB.connect()
    return MongoDB.db

