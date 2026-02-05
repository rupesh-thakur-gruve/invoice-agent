from fastapi import APIRouter, Depends, HTTPException

from core.logger import setup_logger
from schemas.invoice import InvoiceExtractionRequest, InvoiceExtractionResponse
from service.invoice_service import InvoiceService

logger = setup_logger(__name__)

router = APIRouter()

def get_invoice_service() -> InvoiceService:
    return InvoiceService()

@router.post("/invoice", response_model=InvoiceExtractionResponse)
async def extract_invoice(
    request: InvoiceExtractionRequest,
    service: InvoiceService = Depends(get_invoice_service)
):
    """
    Extract invoice data from a base64 encoded file and compare with expected values.
    """
    logger.info("Received invoice extraction request via JSON.")
    
    try:
        result = await service.process_invoice(request)
        return result
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during invoice processing.")