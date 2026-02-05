
import urllib.request
import urllib.error
import json
import os
import time

def verify_api_comparison():
    url = "http://127.0.0.1:8000/extract/invoice"
    file_path = "test_invoice.pdf"
    
    if not os.path.exists(file_path):
        print(f"Creating dummy PDF at {file_path}")
        with open(file_path, "wb") as f:
             f.write(b"%PDF-1.0\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n149\n%%EOF")

    print(f"Testing API at {url} with {file_path} and comparision data")
    
    # Boundary for multipart/form-data
    boundary = '---boundary'
    body_parts = []
    
    # helper for adding fields
    def add_field(name, value):
        body_parts.append(f'--{boundary}')
        body_parts.append(f'Content-Disposition: form-data; name="{name}"')
        body_parts.append('')
        body_parts.append(str(value))

    # Add form fields (comparison data)
    add_field("CP_Name", "Test Partner")
    add_field("PAN", "ABCDE1234F")
    add_field("GSTIN", "27ABCDE1234F1Z5")
    # Sending a matching numeric value
    add_field("Total_Invoice_Amount", "1000.00")

    # Add File
    body_parts.append(f'--{boundary}')
    body_parts.append(f'Content-Disposition: form-data; name="file"; filename="{file_path}"')
    body_parts.append('Content-Type: application/pdf')
    body_parts.append('')
    
    with open(file_path, "rb") as f:
        body_parts.append(f.read().decode('latin-1'))
        
    body_parts.append(f'--{boundary}--')
    body_parts.append('')
    
    body = '\r\n'.join(body_parts).encode('latin-1')
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
            # Pretty print the json response
            try:
                resp_json = json.loads(response_text)
                print(f"Response:\n{json.dumps(resp_json, indent=2)}")
                
                # Assertions
                if "comparisons" in resp_json:
                    print("SUCCESS: 'comparisons' key found.")
                else:
                    print("FAILURE: 'comparisons' key missing.")
                
                if "score" in resp_json:
                     print(f"SUCCESS: 'score' key found. Value: {resp_json['score']}")
                else:
                     print("FAILURE: 'score' key missing.")

                if "remarks" in resp_json:
                     print(f"SUCCESS: 'remarks' key found. Value: {resp_json['remarks']}")
                else:
                     print("FAILURE: 'remarks' key missing.")

                if "recommendedAction" in resp_json:
                     print(f"SUCCESS: 'recommendedAction' key found. Value: {resp_json['recommendedAction']}")
                else:
                     print("FAILURE: 'recommendedAction' key missing.")

            except json.JSONDecodeError:
                print(f"Response Text (Not JSON): {response_text}")

            
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    verify_api_comparison()
