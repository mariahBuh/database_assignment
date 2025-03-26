from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
import motor.motor_asyncio
import os
from dotenv import load_dotenv

# Creating FastAPI instance
app = FastAPI()

# Loading environment variables fron the .env file
load_dotenv()

# Get MongoDB credentials
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
MONGO_URI = f"mongodb+srv://{username}:{password}@dbe.t4lj7.mongodb.net/game_db?retryWrites=true&w=majority"

# Connect to MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client.game_db

# Root endpoint to confirm the API is running
@app.get("/")
async def root():
    return {"message": "Server is running!"}

# Pydantic model for validating player score input
class PlayerScore(BaseModel):
    player_id: str  # Unique identifier for the player
    score: int # Score achieved by the player

# Endpoint to upload a sprite file to the 'sprites' collection
@app.post("/upload_sprite")
async def upload_sprite(file: UploadFile = File(...)):
    """Accepts a sprite file via form-data and stores it in the MongoDB 'sprites' collection.
    The file content is saved in binary along with its original filename."""

    try:
        content = await file.read()
        sprite_doc = {"filename": file.filename, "content": content}
        result = await db.sprites.insert_one(sprite_doc)
        return {"message": "Sprite uploaded", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Upload failed")

# Endpoint to upload an audio file to the 'audio_files' collection

@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...)):
    """Accepts an audio file via form-data and stores it in the MongoDB 'audio_files' collection.
    The file content is saved in binary format along with its filename."""
    try:
        content = await file.read()
        audio_doc = {"filename": file.filename, "content": content}
        result = await db.audio_files.insert_one(audio_doc)
        return {"message": "Audio file uploaded", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Upload failed")

# Endpoint to record a player's score in the 'scores' collection
@app.post("/player_score")
async def add_score(score: PlayerScore):
    """Accepts a JSON object with player_id and score.
    Validates the input using Pydantic and stores it in the 'scores' collection in MongoDB."""
    try:
        score_doc = {"player_id": str(score.player_id), "score": score.score}
        result = await db.scores.insert_one(score_doc)
        return {"message": "Score recorded", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Insert failed")
