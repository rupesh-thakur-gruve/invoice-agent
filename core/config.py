
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings:
    """Application settings and constants."""
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INPUT_DIR = os.getenv("INPUT_DIR", os.path.join(BASE_DIR, "input_pdfs"))
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.join(BASE_DIR, "output_json"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # OCR Settings
    OCR_DPI = int(os.getenv("OCR_DPI", "300"))
    SCANNED_PDF_THRESHOLD = int(os.getenv("SCANNED_PDF_THRESHOLD", "10"))

    # Extraction Regex Patterns
    EXTRACTION_PATTERNS = {
        "CP_Name": os.getenv("REGEX_CP_NAME", r"Channel Partner\s*\(Bill From\)\s*[:\-]?\s*(.+?)(?=\s+(?:PAN|GSTIN|Address|Email|Mob|Contact|S\.No|Sr|Plot|Shop|Flat|Suite|Phase|Sector|Near|Opp|Behind)|$)"),
        "PAN": os.getenv("REGEX_PAN", r"\bPAN\s*[:\-]?\s*([A-Z]{5}[0-9]{4}[A-Z])\b"),
        "GSTIN": os.getenv("REGEX_GSTIN", r"\bGSTIN\s*[:\-]?\s*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z])\b"),
        "Agreement_Amount": os.getenv("REGEX_AGREEMENT_AMOUNT", r"Agreement Value\s*(?:Amount)?\s*[:\-]?\s*[₹■]?\s*([\d,]+\.\d{2})"),
        "Brokerage_Amount": r"(?:Commission|Brokerage)\s*@?\s*[\d\.]+\s*%?\s*(?:Amount|Value)?\s*[:\-]?\s*[₹■]?\s*([\d,]+(?:\.\d{1,2})?)",
        "CGST": os.getenv("REGEX_CGST", r"CGST\s*@?\s*9%\s*[:\-]?\s*[₹■]?\s*([\d,]+\.\d+)"),
        "SGST": os.getenv("REGEX_SGST", r"SGST\s*@?\s*9%\s*[:\-]?\s*[₹■]?\s*([\d,]+\.\d+)"),
        "Total_Invoice_Amount": os.getenv("REGEX_TOTAL_AMOUNT", r"Total Invoice Amount\s*[:\-]?\s*[:\-]?\s*[₹■]?\s*([\d,]+\.\d+)"),
        "TDS": r"TDS\s*(?:u/s\s*194H)?\s*(?:@?\s*[\d\.]+\s*%?)?\s*[:\-]?\s*[₹■]?\s*([\d,]+(?:\.\d{1,2})?)",
    }

    # Scoring Weights
    WEIGHT_CP_NAME = int(os.getenv("WEIGHT_CP_NAME", "5"))
    WEIGHT_PAN = int(os.getenv("WEIGHT_PAN", "15"))
    WEIGHT_GSTIN = int(os.getenv("WEIGHT_GSTIN", "15"))
    WEIGHT_AGREEMENT_AMOUNT = int(os.getenv("WEIGHT_AGREEMENT_AMOUNT", "15"))
    WEIGHT_BROKERAGE_AMOUNT = int(os.getenv("WEIGHT_BROKERAGE_AMOUNT", "20"))
    WEIGHT_GST_BREAKUP = int(os.getenv("WEIGHT_GST_BREAKUP", "10"))
    WEIGHT_TDS = int(os.getenv("WEIGHT_TDS", "10"))
    WEIGHT_TOTAL_AMOUNT = int(os.getenv("WEIGHT_TOTAL_AMOUNT", "10"))

    # Decision Thresholds
    THRESHOLD_AUTO_APPROVE = int(os.getenv("THRESHOLD_AUTO_APPROVE", "90"))
    THRESHOLD_REVIEW = int(os.getenv("THRESHOLD_REVIEW", "70"))

settings = Settings()
