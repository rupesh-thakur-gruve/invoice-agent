import base64
import json
import os
import shutil
import uuid
from typing import Any, Dict, List, Optional

from core.config import settings
from core.logger import setup_logger
from schemas.invoice import ComparisonValue, InvoiceExtractionRequest, InvoiceExtractionResponse
from service.invoice_extractor import process_invoice_from_path
from service.scoring import calculate_score

logger = setup_logger(__name__)

def normalize_value(val: Any) -> Any:
    """Normalize string or float values for comparison."""
    if val is None:
        return ""
    val = str(val).strip()
    try:
        # Try to convert to float for numeric comparison
        # Remove commas and currency symbols if present
        cleaned = val.replace(",", "").replace("₹", "").replace("■", "").strip()
        float_val = float(cleaned)
        return float_val
    except ValueError:
        return val.lower()

def compare_field(expected: Optional[str], actual: Optional[str]) -> Dict[str, Any]:
    """Compare two values and return result object."""
    if normalize_value(expected) == normalize_value(actual):
        return {"expected": expected, "actual": actual, "result": "MATCH"}
    else:
        return {"expected": expected, "actual": actual, "result": "DISCREPANCY"}

class InvoiceService:
    def __init__(self):
        # Ensure directories exist
        os.makedirs(settings.INPUT_DIR, exist_ok=True)
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)

    async def process_invoice(self, request: InvoiceExtractionRequest) -> InvoiceExtractionResponse:
        logger.info("Starting invoice processing in InvoiceService.")
        
        file_path = ""
        original_filename = ""
        
        try:
            # Handle Base64 String
            blob_64 = request.blob_64
            try:
                # 1. Strip Data URL prefix if present
                if "," in blob_64:
                    blob_64 = blob_64.split(",")[-1]
                
                # 2. Clean whitespace/newlines
                blob_64 = blob_64.strip()

                # 3. Fix missing padding
                missing_padding = len(blob_64) % 4
                if missing_padding:
                    blob_64 += "=" * (4 - missing_padding)

                # 4. Decode
                decoded_data = base64.b64decode(blob_64)
                
                # 5. Sniff extension based on signature
                extension = ".txt" # Default
                if decoded_data.startswith(b"%PDF"):
                    extension = ".pdf"
                elif decoded_data.startswith(b"PK\x03\x04"):
                    extension = ".docx"
                elif b"," in decoded_data[:200]: # Heuristic for CSV
                    extension = ".csv"
                
                # Generate a unique filename with detected extension
                original_filename = f"blob_{uuid.uuid4().hex}{extension}"
                file_path = os.path.join(settings.INPUT_DIR, original_filename)
                
                with open(file_path, "wb") as buffer:
                    buffer.write(decoded_data)
                logger.info(f"Base64 blob decoded and saved as {extension} at {file_path}")
                
            except Exception as e:
                logger.error(f"Base64 decoding failed: {str(e)}")
                raise ValueError(f"Invalid Base64 string or format: {str(e)}")

            # Process the file
            try:
                extracted_data = process_invoice_from_path(file_path)
            except Exception as e:
                logger.error(f"Failed to process invoice: {str(e)}")
                raise RuntimeError(f"Failed to process invoice: {str(e)}")

            # Perform Comparison
            extracted_fields = extracted_data.get("extracted_fields", {})
            
            comparisons_raw = {
                "CP_Name": compare_field(request.CP_Name, extracted_fields.get("CP_Name")),
                "PAN": compare_field(request.PAN, extracted_fields.get("PAN")),
                "GSTIN": compare_field(request.GSTIN, extracted_fields.get("GSTIN")),
                "Agreement_Amount": compare_field(request.Agreement_Amount, extracted_fields.get("Agreement_Amount")),
                "Brokerage_Amount": compare_field(request.Brokerage_Amount, extracted_fields.get("Brokerage_Amount")),
                "CGST": compare_field(request.CGST, extracted_fields.get("CGST")),
                "SGST": compare_field(request.SGST, extracted_fields.get("SGST")),
                "Total_Invoice_Amount": compare_field(request.Total_Invoice_Amount, extracted_fields.get("Total_Invoice_Amount")),
                "TDS": compare_field(request.TDS, extracted_fields.get("TDS")),
            }
            
            comparisons = {k: ComparisonValue(**v) for k, v in comparisons_raw.items()}

            # Calculate Score
            score_result = calculate_score(comparisons_raw)
            
            result_data = {
                "comparisons": comparisons,
                "score": score_result.get("score"),
                "remarks": score_result.get("remarks"),
                "recommendedAction": score_result.get("recommendedAction")
            }
            
            # Save result to output_json/ (Optional, but kept for parity with old code)
            base_filename = os.path.splitext(original_filename)[0]
            output_filename = f"{base_filename}.json"
            output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
            
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    # Need to serialize slightly differently for ComparisonValue objects
                    json_data = {
                        "comparisons": {k: v.model_dump() for k, v in comparisons.items()},
                        "score": result_data["score"],
                        "remarks": result_data["remarks"],
                        "recommendedAction": result_data["recommendedAction"]
                    }
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.warning(f"Failed to save result JSON: {str(e)}")

            # Cleanup
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup files: {str(e)}")

            return InvoiceExtractionResponse(**result_data)

        except Exception as e:
            # Ensure cleanup on failure if file_path was set
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            raise e
