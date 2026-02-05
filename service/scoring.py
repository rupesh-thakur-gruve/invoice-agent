from typing import Any, Dict, List

from core.logger import setup_logger

logger = setup_logger(__name__)

def calculate_score(comparisons: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate the confidence score based on field matches.
    
    Weights:
    - CP Name Match: 5
    - PAN Match: 15
    - GSTIN Match: 15
    - Agreement Amount Match: 15
    - Brokerage Calculation: 20
    - GST Breakup Validation (CGST & SGST): 10
    - TDS Validation: 10
    - Total Invoice Amount Match: 10
    
    Decision Logic:
    - Score >= 90 & No Hard Stop -> AUTO_APPROVE
    - Score 70-89 & No Hard Stop -> REVIEW
    - Score < 70 OR Hard Stop -> REJECT
    """
    logger.info("Calculating score for comparison results...")
    
    score = 0
    hard_stop_triggered = False
    hard_stop_reasons: List[str] = []
    failed_fields: List[str] = []

    # Helper to check match
    def is_match(field: str) -> bool:
        match = comparisons.get(field, {}).get("result") == "MATCH"
        if match:
            logger.debug(f"Field '{field}' matched.")
        else:
            logger.debug(f"Field '{field}' did NOT match.")
            failed_fields.append(field)
        return match

    # 1. CP Name Match (5 points)
    if is_match("CP_Name"):
        score += 5

    # 2. PAN Match (15 points) - HARD STOP
    if is_match("PAN"):
        score += 15
    else:
        hard_stop_triggered = True
        hard_stop_reasons.append("PAN mismatch")

    # 3. GSTIN Match (15 points) - HARD STOP
    if is_match("GSTIN"):
        score += 15
    else:
        hard_stop_triggered = True
        hard_stop_reasons.append("GSTIN mismatch")

    # 4. Agreement Amount Match (15 points) - HARD STOP
    if is_match("Agreement_Amount"):
        score += 15
    else:
        hard_stop_triggered = True
        hard_stop_reasons.append("Agreement Amount mismatch")

    # 5. Brokerage Calculation (20 points)
    if is_match("Brokerage_Amount"):
        score += 20

    # 6. GST Breakup Validation (10 points) - Both CGST and SGST must match
    if is_match("CGST") and is_match("SGST"):
        score += 10
    elif not is_match("CGST") or not is_match("SGST"):
       # Logic already captured by is_match calling failed_fields append
       pass


    # 7. TDS Validation (10 points)
    if is_match("TDS"):
        score += 10

    # 8. Total Invoice Amount Match (10 points)
    if is_match("Total_Invoice_Amount"):
        score += 10

    # Determine Decision and Recommended Action
    decision = ""
    recommended_action = ""
    
    if hard_stop_triggered:
        decision = "REJECT"
        recommended_action = "REJECT AND RETURN TO CHANNEL PARTNER"
    elif score >= 90:
        decision = "AUTO_APPROVE"
        recommended_action = "AUTO APPROVE"
    elif 70 <= score <= 89:
        decision = "REVIEW"
        recommended_action = "MANUAL REVIEW REQUIRED"
    else:
        decision = "REJECT"
        recommended_action = "REJECT AND RETURN TO CHANNEL PARTNER"

    # Generate Remarks
    remarks_parts = [f"Invoice validation resulted in a score of {score}."]
    
    if hard_stop_triggered:
        remarks_parts.append(f"Critical discrepancies were found in: {', '.join(hard_stop_reasons)}.")
        remarks_parts.append("This requires rejection as per policy.")
    elif score < 90:
        if failed_fields:
             remarks_parts.append(f"Discrepancies found in: {', '.join(failed_fields)}.")
        remarks_parts.append("Score is below approval threshold.")
    else:
        remarks_parts.append("All critical financial details and identifiers matched successfully.")

    remarks = " ".join(remarks_parts)

    logger.info(f"Score calculation complete. Score: {score}, Decision: {decision}")
    
    return {
        "score": str(score),
        "remarks": remarks,
        "recommendedAction": recommended_action
    }
