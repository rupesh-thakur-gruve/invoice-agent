
import urllib.request
import urllib.error
import json
import os
import time
import subprocess
import sys
import mimetypes

def verify_api():
    # Start the server
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--port", "8000"], cwd=os.getcwd())
    print("Server started with PID:", proc.pid)
    
    try:
        # Wait for server to start
        time.sleep(5)
        
        url = "http://127.0.0.1:8000/extract/invoice"
        file_path = "test_invoice.pdf"
        
        # Prepare multipart/form-data
        boundary = '---boundary'
        data = []
        
        data.append(f'--{boundary}')
        data.append(f'Content-Disposition: form-data; name="file"; filename="{file_path}"')
        data.append('Content-Type: application/pdf')
        data.append('')
        
        with open(file_path, "rb") as f:
            data.append(f.read().decode('latin-1'))
            
        data.append(f'--{boundary}--')
        data.append('')
        
        body = '\r\n'.join(data).encode('latin-1')
        headers = {
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Content-Length': len(body)
        }
        
        req = urllib.request.Request(url, data=body, headers=headers)
        
        try:
            with urllib.request.urlopen(req) as response:
                status_code = response.getcode()
                response_text = response.read().decode('utf-8')
                
                print(f"Status Code: {status_code}")
                print(f"Response: {response_text}")
                
                if status_code == 200:
                    print("SUCCESS: API call returned 200 OK")
                    resp_json = json.loads(response_text)
                    if "file_name" in resp_json and "extracted_fields" in resp_json:
                        print("SUCCESS: Response structure is correct")
                    else:
                        print("FAILURE: Response structure incorrect")
                else:
                    print("FAILURE: API call failed")
                    
        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code} - {e.reason}")
            print(e.read().decode('utf-8'))
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}")

        # Check if file saved
        if os.path.exists("input_pdfs/test_invoice.pdf"):
            print("SUCCESS: Input PDF saved")
        else:
            print("FAILURE: Input PDF not saved")
            
        # Check if output json saved
        expected_json = "output_json/test_invoice.json"
        if os.path.exists(expected_json):
            print("SUCCESS: Output JSON saved")
        else:
            print("FAILURE: Output JSON not saved")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Kill the server
        proc.terminate()
        proc.wait()
        print("Server stopped")

if __name__ == "__main__":
    verify_api()
