from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb://mongo:UmxHXTOOXKBaiFQUnsawgcTQSmwkOHBw@autorack.proxy.rlwy.net:54479/"
DATABASE_NAME = "cursor1"

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME] 
