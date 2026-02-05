
import os

class Settings:
    """Application settings and constants."""
    
    # Paths (using absolute paths or relative to project root)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INPUT_DIR = os.path.join(BASE_DIR, "input_pdfs")
    OUTPUT_DIR = os.path.join(BASE_DIR, "output_json")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # LLM Settings
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

settings = Settings()
