import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in .env file")

    # Model Configuration
    MODEL_NAME = "gemini-2.5-pro" # Using Pro for higher visual reasoning capabilities
    TEMPERATURE = 0.0
    
    # Processing Configuration
    CHUNK_SIZE = 1  # Number of pages to send to Gemini in one request (Batching)
    TOTAL_PAGES_TO_PROCESS = None  # None = Process all, Integer = Limit
    DPI = 300  # High resolution for small text details
    
    # Paths
    BASE_DIR = Path(__file__).parent
    TEMP_DIR = BASE_DIR / "temp"
    OUTPUT_DIR = BASE_DIR / "output"
    
    # Ensure directories exist
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # config.py - Add this line inside Config class
    POPPLER_PATH = r"C:\Program Files\poppler-25.12.0\Library\bin"

# Schema Definition
VOTER_SCHEMA = {
    "type": "object",
    "properties": {
        "serial_no": {"type": ["string", "null"]},
        "voter_name": {"type": ["string", "null"]},
        "relative_name": {"type": ["string", "null"]},
        "gender": {"type": ["string", "null"], "enum": ["पुरुष", "स्त्री", None]},
        "age": {"type": ["string", "null"]},
        "house_no": {"type": ["string", "null"]},
        "voter_id": {"type": ["string", "null"]},
        "area_code": {"type": ["string", "null"]},
        "photo_available": {"type": "boolean"}
    },
    "required": ["serial_no", "voter_id"]
}