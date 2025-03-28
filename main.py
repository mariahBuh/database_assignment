# Imports Required Libraries
from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel, Field, field_validator
import re
import motor.motor_asyncio
import os
from dotenv import load_dotenv
import base64

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

# Allowed extensions for image and audio files
Allowed_Image_Extentions = {".png", ".jpg", ".jpeg", ".gif"}
Allowed_Audio_Extentions = {".mp3", ".wav", ".ogg"}

# Adding code to prevent SQL Injections for the file extensions
def validate_file_upload(file: UploadFile, allowed_extensions: set):
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()

    # Check if the file extension is allowed
    if not ext or ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {ext}. Allowed types are: {', '.join(allowed_extensions)}"
        )


# Pydantic model for validating player score input (Preventing SQL Injection)
class PlayerScore(BaseModel):
    player_id: str   = Field(..., min_length=1, max_length=50) # Unique identifier for the player
    score: int = Field(..., ge=0) # Score achieved by the player

    
    # Block dangerous characters (like $ or .)
    @field_validator("player_id")
    def no_special_chars(cls, v):

        # Check if the player_id contains only alphanumeric characters, underscores, spaces, or hyphens
        if not re.match("^[a-zA-Z0-9_ -]+$", v):
            raise ValueError("Player ID contains invalid characters")
        return v

    class Config:
        extra = "forbid"  #Blocks extra unexpected fields

# Endpoint to upload a sprite file to the 'sprites' collection
@app.post("/upload_sprite")
async def upload_sprite(file: UploadFile = File(...)):
    """Accepts a sprite file via form-data and stores it in the MongoDB 'sprites' collection.
    The file content is saved in binary along with its original filename."""

    try:
        # Validate the file extension using the allowed extensions set
        validate_file_upload(file, Allowed_Image_Extentions)

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
        # Validate the file extension using the allowed extensions set
        validate_file_upload(file, Allowed_Audio_Extentions)

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
    

################################## Retrieve data from MongoDB ##################################
 
# Retrieve all uploaded sprite files from the 'sprites' collection.
# Each sprite includes a filename and a base64-encoded version of its binary content.
@app.get("/sprites")
async def get_sprites():
    try:
        sprites = []
        cursor = db.sprites.find()
        async for doc in cursor:
            doc["_id"] = str(doc["_id"]) # Convert ObjectId to string for JSON serialization
            if "content" in doc:
                # Encode binary content to base64 string for JSON response
                doc["content"] = base64.b64encode(doc["content"]).decode("utf-8")
            sprites.append(doc)
        return sprites
    except Exception as e:
         # Log error and return internal server error
        import traceback
        print("ERROR in /sprites:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Sprite retrieval failed")

# Retrieve all uploaded audio files from the 'audio_files' collection.
# Each audio includes a filename and a base64-encoded version of its binary content.
@app.get("/audios")
async def get_audios():
    try:
        audios = []
        cursor = db.audio_files.find()
        async for doc in cursor:
            doc["_id"] = str(doc["_id"]) # Convert ObjectId to string for JSON serialization

            if "content" in doc:
                # Encode binary content to base64 string for JSON response
                doc["content"] = base64.b64encode(doc["content"]).decode("utf-8")
            audios.append(doc)
        return audios
    except Exception as e:
        # Log error and return internal server error
        import traceback
        print("ERROR in /audios:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Audio retrieval failed")

# Retrieve all player scores from the 'scores' collection.
# Each record includes the player's ID and their score value.
@app.get("/scores")
async def get_scores():
    scores = []
    cursor = db.scores.find()
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
        scores.append(doc)
    return scores
