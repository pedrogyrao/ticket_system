from motor.motor_asyncio import AsyncIOMotorClient

from .mongodb import database


async def connect_to_mongo():
    database.client = AsyncIOMotorClient(str("localhost:27017"),
                                   maxPoolSize=10,
                                   minPoolSize=10)

    database.ticketDB = database.client.tancho_ci_db.ticket


async def close_mongo_connection():
    database.client.close()
