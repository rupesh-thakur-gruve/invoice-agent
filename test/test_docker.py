
import base64
import json
import requests
import os

def verify_api_remote():
    url = "http://127.0.0.1:9090/extract/invoice"
    # Search for any PDF in input_pdfs
    pdf_files = [f for f in os.listdir("input_pdfs") if f.endswith(".pdf")]
    if not pdf_files:
        print("No PDF files found in input_pdfs/ for testing.")
        return
    
    file_path = os.path.join("input_pdfs", pdf_files[0])
    print(f"Testing API at {url} with {file_path}")
    
    try:
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
            blob_64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        payload = {
            "blob_64": blob_64,
            "CP_Name": "Sample Partner",
            "PAN": "ABCDE1234F"
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        print("Sending POST request to /extract/invoice...")
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS: API returned 200 OK")
            print("Response JSON:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"FAILURE: API returned {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    verify_api_remote()
