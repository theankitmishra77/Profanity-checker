from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os

# Initialize FastAPI app
app = FastAPI()

# Sapling API settings
API_KEY= os.environ.get("API_KEY")
API_URL= os.environ.get("API_URL")
# SAPLING_API_KEY = "SICCY2TMCVS8EI95UEQL7NVZVG2JZCGU"
# SAPLING_API_URL = "https://api.sapling.ai/api/v1/profanity"

# Request Model
class TextInput(BaseModel):
    text: str

# Preprocessing function to normalize obfuscated words
def preprocess_text(text: str) -> str:
    """
    Normalize obfuscated text by replacing common obfuscation patterns.
    """
    substitutions = {
        "@": "a",
        "3": "e",
        "!": "i",
        "1": "i",
        "$": "s",
        "0": "o"
    }
    # Replace each obfuscation pattern
    for key, value in substitutions.items():
        text = text.replace(key, value)
    return text

# Profanity Filtering Endpoint
@app.post("/filter_profanity")
def filter_profanity(input_text: TextInput):
    """
    Endpoint to filter profanity using Sapling AI.
    """
    # Preprocess the input text to handle obfuscation
    normalized_text = preprocess_text(input_text.text)
    
    # Prepare payload for Sapling API
    payload = {
        "key": SAPLING_API_KEY,
        "text": normalized_text
    }

    # Send request to Sapling API
    response = requests.post(SAPLING_API_URL, json=payload)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error communicating with the API.")

    sapling_response = response.json()

    toks = sapling_response.get("toks", [])
    labels = sapling_response.get("labels", [])

    # Identify profane words
    profane_words = [toks[i] for i in range(len(labels)) if labels[i] == 1]

    # Generate censored text
    censored_toks = [
        "*" * len(toks[i]) if labels[i] == 1 else toks[i]
        for i in range(len(toks))
    ]
    censored_text = " ".join(censored_toks)

    # Construct the output
    result = {
        "is_profane": len(profane_words) > 0,
        "profane_words": profane_words,
        "censored_text": censored_text
    }
    return result

# Example Root Endpoint
@app.get("/")
def read_root():
    return {"message": "Profanity Filter API"}

