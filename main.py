from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import motor.motor_asyncio

app = FastAPI()
username = "admin"
password = "mcast"

# Connect to MongoDB Atlas
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://{username}:{password}@dbe.t4lj7.mongodb.net/")
db = client.multimedia_db

# Data model for player scores
class PlayerScore(BaseModel):
    player_id: int
    score: int

# Upload sprite
@app.post("/upload_sprite")
async def upload_sprite(file: UploadFile = File(...)):
    content = await file.read()
    sprite_doc = {"filename": file.filename, "content": content}
    result = await db.sprites.insert_one(sprite_doc)
    return {"message": "Sprite uploaded", "id": str(result.inserted_id)}

# Upload audio
@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...)):
    content = await file.read()
    audio_doc = {"filename": file.filename, "content": content}
    result = await db.audio.insert_one(audio_doc)
    return {"message": "Audio file uploaded", "id": str(result.inserted_id)}

# Add player score
@app.post("/player_score")
async def add_score(score: PlayerScore):
    score_doc = score.dict()
    result = await db.scores.insert_one(score_doc)
    return {"message": "Score recorded", "id": str(result.inserted_id)}
