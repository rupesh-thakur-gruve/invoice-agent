
import urllib.request
import urllib.error
import json
import os
import time

def verify_api_remote():
    url = "http://127.0.0.1:8000/extract/invoice"
    file_path = "test_invoice.pdf"
    
    print(f"Testing API at {url} with {file_path}")
    
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
        print("Make sure the Docker container is running and port 8000 is exposed.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    verify_api_remote()
