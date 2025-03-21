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
try:
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client.game_db
    print("Connected to MongoDB successfully!")
except Exception as e:
    print("MongoDB Connection Failed")

#Test FastAPI is running
@app.get("/")
async def root():
    return {"message": "Server is running!"}

#Player Score Model
class PlayerScore(BaseModel):
    player_id: str
    score: int


#Upload Sprite Endpoint
@app.post("/upload_sprite")
async def upload_sprite(file: UploadFile = File(...)):
    try:
        print("Uploading sprite:", file.filename)
        content = await file.read()
        print("File content length:", len(content))
        sprite_doc = {"filename": file.filename, "content": content}
        result = await db.sprites.insert_one(sprite_doc)
        print("Sprite Uploaded Successfully:", result.inserted_id)
        return {"message": "Sprite uploaded", "id": str(result.inserted_id)}
    except Exception as e:
        print("Error uploading sprite")
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

#Upload Audio Endpoint
@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...)):

    try:
        print("Uploading audio:", file.filename)
        content = await file.read()
        print("File content length:", len(content))
        audio_doc = {"filename": file.filename, "content": content}
        result = await db.audio_files.insert_one(audio_doc)
        print("Audio Uploaded Successfully:")
        return {"message": "Audio file uploaded", "id": str(result.inserted_id)}
    except Exception as e:
        print("Error uploading audio")
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

@app.post("/player_score")
async def add_score(score: PlayerScore):
    try:
        print("Received player score data:", score)
        score_doc = {"player_id": str(score.player_id), "score": score.score}
        print("Inserting into MongoDB:", score_doc)
        result = await db.scores.insert_one(score_doc)
        print("Score Recorded Successfully:", result.inserted_id)
        return {"message": "Score recorded", "id": str(result.inserted_id)}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Insert failed: {e}")