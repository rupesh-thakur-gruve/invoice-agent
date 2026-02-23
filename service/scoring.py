from typing import Any, Dict, List

from core.config import settings
from core.logger import setup_logger

logger = setup_logger(__name__)

def calculate_score(comparisons: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate the confidence score based on field matches.
    
    Weights and thresholds are loaded from settings.
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

    # 1. CP Name Match
    if is_match("CP_Name"):
        score += settings.WEIGHT_CP_NAME

    # 2. PAN Match - HARD STOP
    if is_match("PAN"):
        score += settings.WEIGHT_PAN
    else:
        hard_stop_triggered = True
        hard_stop_reasons.append("PAN mismatch")

    # 3. GSTIN Match - HARD STOP
    if is_match("GSTIN"):
        score += settings.WEIGHT_GSTIN
    else:
        hard_stop_triggered = True
        hard_stop_reasons.append("GSTIN mismatch")

    # 4. Agreement Amount Match - HARD STOP
    if is_match("Agreement_Amount"):
        score += settings.WEIGHT_AGREEMENT_AMOUNT
    else:
        hard_stop_triggered = True
        hard_stop_reasons.append("Agreement Amount mismatch")

    # 5. Brokerage Calculation
    if is_match("Brokerage_Amount"):
        score += settings.WEIGHT_BROKERAGE_AMOUNT

    # 6. GST Breakup Validation - Both CGST and SGST must match
    if is_match("CGST") and is_match("SGST"):
        score += settings.WEIGHT_GST_BREAKUP
    elif not is_match("CGST") or not is_match("SGST"):
       # Logic already captured by is_match calling failed_fields append
       pass


    # 7. TDS Validation
    if is_match("TDS"):
        score += settings.WEIGHT_TDS

    # 8. Total Invoice Amount Match
    if is_match("Total_Invoice_Amount"):
        score += settings.WEIGHT_TOTAL_AMOUNT

    # Determine Decision and Recommended Action
    decision = ""
    recommended_action = ""
    
    if hard_stop_triggered:
        decision = "REJECT"
        recommended_action = "REJECT AND RETURN TO CHANNEL PARTNER"
    elif score >= settings.THRESHOLD_AUTO_APPROVE:
        decision = "AUTO_APPROVE"
        recommended_action = "AUTO APPROVE"
    elif settings.THRESHOLD_REVIEW <= score < settings.THRESHOLD_AUTO_APPROVE:
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
