
import base64
import json
import requests
import os

def run_test_scenario(url, blob_64, scenario_name, expected_fields):
    print(f"\n" + "="*50)
    print(f"SCENARIO: {scenario_name}")
    print("="*50)
    
    payload = {
        "blob_64": blob_64,
        **expected_fields
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            comparisons = result.get("comparisons", {})
            
            all_match = True
            print("\nComparisons:")
            print(f"{'Field':20} | {'Result':12} | {'Expected':20} | {'Actual':20}")
            print("-" * 80)
            for field, data in comparisons.items():
                match_status = data.get('result')
                if match_status != "MATCH":
                    all_match = False
                
                print(f"{field:20} | {match_status:12} | {str(data.get('expected')):20} | {str(data.get('actual')):20}")
            
            print(f"\nFinal Verdict: {'✅ ALL FIELDS MATCH' if all_match else '❌ DISCREPANCIES FOUND'}")
            print(f"Score: {result.get('score')}")
            print(f"Remarks: {result.get('remarks')}")
            print(f"Recommended Action: {result.get('recommendedAction')}")
            
            return all_match
        else:
            print(f"FAILURE: API returned {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def verify_extraction_scenarios():
    url = "http://127.0.0.1:9090/extract/invoice"
    pdf_path = "input_pdfs/blob_b70363930400458681d4a18f71e100d7.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found at {pdf_path}")
        return
    
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
        blob_64 = base64.b64encode(pdf_bytes).decode('utf-8')

    # Define Scenarios
    scenarios = [
        {
            "name": "All Fields Match",
            "expected": {
                "CP_Name": "Shree Ganesh Realty Baner",
                "PAN": "AABCS1234F",
                "GSTIN": "27AABCS1234F1Z5",
                "Agreement_Amount": "7,89,600.00",
                "Brokerage_Amount": None,
                "CGST": "1776.6",
                "SGST": "1776.6",
                "Total_Invoice_Amount": "23,293.2",
                "TDS": "987"
            }
        },
        {
            "name": "Some Fields Match",
            "expected": {
                "CP_Name": "Shree Ganesh Realty Baner",
                "PAN": "WRONG_PAN_123",
                "GSTIN": "WRONG_GSTIN_456",
                "Agreement_Amount": "7,89,600.00",
                "Brokerage_Amount": "100.00", # Wrong
                "CGST": "1776.6",
                "SGST": "1776.6",
                "Total_Invoice_Amount": "0.00", # Wrong
                "TDS": "987"
            }
        },
        {
            "name": "No Fields Match",
            "expected": {
                "CP_Name": "Unknown Corp",
                "PAN": "XXXXX0000X",
                "GSTIN": "00XXXXX0000X0Z0",
                "Agreement_Amount": "1.00",
                "Brokerage_Amount": "1.00",
                "CGST": "1.00",
                "SGST": "1.00",
                "Total_Invoice_Amount": "1.00",
                "TDS": "1.00"
            }
        }
    ]

    for scenario in scenarios:
        run_test_scenario(url, blob_64, scenario["name"], scenario["expected"])

if __name__ == "__main__":
    verify_extraction_scenarios()
