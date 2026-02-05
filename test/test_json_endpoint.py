import base64
import json
import requests
import time
import subprocess
import os
import signal

def test_json_endpoint():
    # Start the server
    proc = subprocess.Popen(["./venv/bin/python", "-m", "uvicorn", "main:app", "--port", "8000"])
    print(f"Server started with PID: {proc.pid}")
    
    try:
        # Wait for server to start
        time.sleep(5)
        
        url = "http://127.0.0.1:8000/extract/invoice"
        
        # Create a dummy PDF content or use an existing one if available
        # For testing purposes, we can just send a simple base64 string
        # though the backend sniffs for %PDF
        dummy_pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Title (Test) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
        blob_64 = base64.b64encode(dummy_pdf_content).decode('utf-8')
        
        payload = {
            "blob_64": blob_64,
            "CP_Name": "Test Partner",
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
    finally:
        # Kill the server
        print("Stopping server...")
        os.kill(proc.pid, signal.SIGTERM)
        proc.wait()
        print("Server stopped")

if __name__ == "__main__":
    test_json_endpoint()
