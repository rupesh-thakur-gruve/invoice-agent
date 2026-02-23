
import re
from typing import Dict, Optional

def extract_fields(text: str, patterns: Dict[str, str]) -> Dict[str, Optional[str]]:
    text = re.sub(r"\s+", " ", text)
    extracted = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        value = match.group(1).strip() if match else None
        extracted[key] = value
    return extracted

# Test Patterns (from config.py/ .env refinements)
patterns = {
    "CP_Name": r"Channel Partner\s*\(Bill From\)\s*[:\-]?\s*([\w\s\.\-&]+?)(?=\s+(?:PAN|GSTIN|Address|Email|Mob|Contact)|$)",
    "PAN": r"\bPAN\s*[:\-]?\s*([A-Z]{5}[0-9]{4}[A-Z])\b",
    "GSTIN": r"\bGSTIN\s*[:\-]?\s*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z])\b",
    "Agreement_Amount": r"Agreement Value\s*(?:Amount)?\s*[:\-]?\s*[₹■]?\s*([\d,]+\.\d{2})",
    "Brokerage_Amount": r"(?:Commission|Brokerage)\s*@?\s*[\d\.]+\s*%?\s*(?:Amount|Value)?\s*[:\-]?\s*[₹■]?\s*([\d,]+(?:\.\d{1,2})?)",
    "CGST": r"CGST\s*@?\s*9%\s*[:\-]?\s*[₹■]?\s*([\d,]+\.\d+)",
    "SGST": r"SGST\s*@?\s*9%\s*[:\-]?\s*[₹■]?\s*([\d,]+\.\d+)",
    "Total_Invoice_Amount": r"Total Invoice Amount\s*[:\-]?\s*[:\-]?\s*[₹■]?\s*([\d,]+\.\d+)",
    "TDS": r"TDS\s*(?:u/s\s*194H)?\s*(?:@?\s*[\d\.]+\s*%?)?\s*[:\-]?\s*[₹■]?\s*([\d,]+(?:\.\d{1,2})?)"
}

# Sample Text mimicking the problem invoice
sample_text = """
Channel Partner (Bill From) Shree Ganesh Realty Baner 
Address: Baner Road, Pune.
PAN: AABCS1234F
GSTIN: 27AABCS1234F1Z5
Agreement Value Amount: 7,89,600.00
Commission @ 2.5% 19,740
CGST @ 9% 1776.6
SGST @ 9% 1776.6
Total Invoice Amount: 23,293.2
TDS u/s 194H @ 10% 1974
"""

extracted = extract_fields(sample_text, patterns)

print("Extracted Results:")
for k, v in extracted.items():
    print(f"{k:20}: {v}")

# Assertions for known expected values
expected = {
    "CP_Name": "Shree Ganesh Realty",
    "Brokerage_Amount": "19,740",
    "TDS": "1974"
}

# Note: CP_Name might still capture "Baner" if "Address" isn't after it immediately.
# In the sample above, it should stop at "Address".
