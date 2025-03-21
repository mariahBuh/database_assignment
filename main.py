from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
import motor.motor_asyncio
import os
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()

# Get MongoDB credentials
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
MONGO_URI = f"mongodb+srv://{username}:{password}@dbe.t4lj7.mongodb.net/game_db?retryWrites=true&w=majority"

# Connect to MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client.game_db

# FastAPI Root Endpoint
@app.get("/")
async def root():
    return {"message": "Server is running!"}

# Player Score Model
class PlayerScore(BaseModel):
    player_id: str
    score: int

# Upload Sprite Endpoint
@app.post("/upload_sprite")
async def upload_sprite(file: UploadFile = File(...)):
    try:
        content = await file.read()
        sprite_doc = {"filename": file.filename, "content": content}
        result = await db.sprites.insert_one(sprite_doc)
        return {"message": "Sprite uploaded", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Upload failed")

# Upload Audio Endpoint
@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...)):
    try:
        content = await file.read()
        audio_doc = {"filename": file.filename, "content": content}
        result = await db.audio_files.insert_one(audio_doc)
        return {"message": "Audio file uploaded", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Upload failed")

# Add Player Score Endpoint
@app.post("/player_score")
async def add_score(score: PlayerScore):
    try:
        score_doc = {"player_id": str(score.player_id), "score": score.score}
        result = await db.scores.insert_one(score_doc)
        return {"message": "Score recorded", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Insert failed")
