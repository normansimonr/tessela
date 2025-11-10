from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os

# Assuming data_loader and normalization_service are in the same parent directory
from ..data_loader import DataLoader
from ..normalization_service import NormalizationService
from ..config import Config

app = FastAPI()

# Initialize DataLoader and NormalizationService
# In a real application, API key would be loaded securely (e.g., from environment variables)
# and services would be dependency-injected.
data_loader = DataLoader()
normalization_service = NormalizationService(api_key=Config.GEMINI_API_KEY)

class NormalizationRequest(BaseModel):
    book: str
    chapter: int
    verse: int

class NormalizationResponse(BaseModel):
    masoretic: Optional[str]
    vulgate: Optional[str]
    septuagint: Optional[str]

@app.get("/")
async def read_root():
    return {"message": "Verse Normalization API is running"}

@app.get("/verses")
async def get_all_verses():
    """
    Returns a structured list of all unique verses (book, chapter, verse)
    found across all datasets.
    """
    return data_loader.get_all_unique_verses()

@app.post("/normalize", response_model=NormalizationResponse)
async def normalize_verse(request: NormalizationRequest):
    """
    Normalizes a specific verse from all available datasets.
    """
    masoretic_text = data_loader.get_verse(request.book, request.chapter, request.verse, "masoretic")
    septuagint_text = data_loader.get_verse(request.book, request.chapter, request.verse, "septuagint")
    vulgate_text = data_loader.get_verse(request.book, request.chapter, request.verse, "vulgate")

    normalized_masoretic = None
    if masoretic_text:
        normalized_masoretic = normalization_service.normalize_text(masoretic_text)

    normalized_septuagint = None
    if septuagint_text:
        normalized_septuagint = normalization_service.normalize_text(septuagint_text)

    normalized_vulgate = None
    if vulgate_text:
        normalized_vulgate = normalization_service.normalize_text(vulgate_text)

    return NormalizationResponse(
        masoretic=normalized_masoretic,
        vulgate=normalized_vulgate,
        septuagint=normalized_septugint
    )
