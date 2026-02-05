from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class InvoiceExtractionRequest(BaseModel):
    blob_64: str = Field(..., description="Base64 encoded file content")
    CP_Name: Optional[str] = None
    PAN: Optional[str] = None
    GSTIN: Optional[str] = None
    Agreement_Amount: Optional[str] = None
    Brokerage_Amount: Optional[str] = None
    CGST: Optional[str] = None
    SGST: Optional[str] = None
    Total_Invoice_Amount: Optional[str] = None
    TDS: Optional[str] = None

class ComparisonValue(BaseModel):
    expected: Optional[str] = None
    actual: Optional[str] = None
    result: str

class InvoiceExtractionResponse(BaseModel):
    comparisons: Dict[str, ComparisonValue]
    score: str
    remarks: str
    recommendedAction: str
