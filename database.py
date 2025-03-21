import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client["game_db"]
