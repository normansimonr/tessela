import os

class Config:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
    DATA_DIR: str = os.getenv("DATA_DIR", "../../data") # Default path relative to main.py
