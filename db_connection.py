from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb://mongo:UmxHXTOOXKBaiFQUnsawgcTQSmwkOHBw@autorack.proxy.rlwy.net:54479"
client = AsyncIOMotorClient(MONGODB_URL)
db = client.fhir_db
collection = db.rest_patient
