import io
import os
import re
from typing import Any, Dict, Optional

import docx  # python-docx
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

from core.config import settings
from core.logger import setup_logger

logger = setup_logger(__name__)

def extract_text_normal(pdf_path: str) -> str:
    """Extract text from a PDF using PyMuPDF (fitz)."""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        logger.debug(f"Extracted {len(text)} characters using normal extraction.")
        return text.strip()
    except Exception as e:
        logger.error(f"Error in normal text extraction: {str(e)}")
        raise

def extract_text_ocr(pdf_path: str) -> str:
    """Extract text from a PDF using OCR (PyMuPDF -> Image -> Tesseract)."""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page_num, page in enumerate(doc):
            pix = page.get_pixmap(dpi=settings.OCR_DPI)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            page_text = pytesseract.image_to_string(img)
            text += page_text + "\n"
            logger.debug(f"OCR processed page {page_num + 1}")
        logger.debug(f"Extracted {len(text)} characters using OCR.")
        return text.strip()
    except Exception as e:
        logger.error(f"Error in OCR text extraction: {str(e)}")
        raise

def extract_text_docx(file_path: str) -> str:
    """Extract text from a .docx file."""
    try:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return "\n".join(full_text).strip()
    except Exception as e:
        logger.error(f"Error in DOCX text extraction: {str(e)}")
        raise

def extract_text_plain(file_path: str) -> str:
    """Extract text from plain text files (.csv, .txt)."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Error in plain text extraction: {str(e)}")
        raise

def is_scanned_pdf(text: str) -> bool:
    """Detect if a PDF is scanned based on extracted text length."""
    # Threshold for scanned PDF detection
    threshold = settings.SCANNED_PDF_THRESHOLD
    is_scanned = len(text.strip()) < threshold
    if is_scanned:
        logger.info(f"PDF detected as scanned (text length < {threshold}).")
    return is_scanned

def extract_fields(text: str) -> Dict[str, Optional[str]]:
    """Extract fields from text using Regex patterns from settings."""
    text = re.sub(r"\s+", " ", text)
    
    patterns = settings.EXTRACTION_PATTERNS

    extracted = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        value = match.group(1).strip() if match else None
        extracted[key] = value
        logger.debug(f"Extracted {key}: {value}")

    return extracted

def process_invoice_from_path(file_path: str) -> Dict[str, Any]:
    """
    Main function to process an invoice file.
    Routes to appropriate extractor based on file extension.
    """
    logger.info(f"Processing invoice from path: {file_path}")
    
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    extraction_method = ""

    try:
        if ext == ".pdf":
            try:
                text = extract_text_normal(file_path)
                extraction_method = "PyMuPDF"
                if is_scanned_pdf(text):
                    logger.info("Switching to OCR extraction...")
                    text = extract_text_ocr(file_path)
                    extraction_method = "PyMuPDF + OCR"
            except Exception as pdf_error:
                logger.warning(f"PDF processing failed for {file_path}. Falling back to plain text reader. Error: {str(pdf_error)}")
                text = extract_text_plain(file_path)
                extraction_method = "Fallback Text Reader (Corrupt PDF)"
        elif ext in [".docx", ".doc"]:
            text = extract_text_docx(file_path)
            extraction_method = "python-docx"
        elif ext in [".csv", ".txt"]:
            text = extract_text_plain(file_path)
            extraction_method = "Plain Text Reader"
        else:
            # Try plain text as fallback for unknown extensions
            logger.warning(f"Unknown extension {ext}. Attempting plain text extraction.")
            text = extract_text_plain(file_path)
            extraction_method = "Fallback Text Reader"

        extracted_data = extract_fields(text)

        result = {
            "file_name": os.path.basename(file_path),
            "extraction_method": extraction_method,
            "extracted_fields": extracted_data,
            "full_text": text
        }
        return result
    except Exception as e:
        logger.error(f"Failed to process invoice {file_path}: {str(e)}")
        raise
