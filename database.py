from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb+srv://admin:test123@cluster0.ebxwyjk.mongodb.net/wooden_store?retryWrites=true&w=majority"

client = AsyncIOMotorClient(MONGO_URL)
db = client["wooden_store"]

async def test_connection():
    await client.admin.command("ping")
    print("MongoDB Connected ✅")