# Invoice Extraction API Agent

This project implements a REST API for extracting structured data from PDF invoices. It uses FastAPI for the API layer and PyMuPDF + OCR for extraction logic, all containerized with Docker for easy deployment.

## Prerequisites

- **Docker Desktop** (or Docker Engine + Docker Compose) installed on your machine.
- **Git** (optional, for cloning the repository).

## 🚀 Step-by-Step Setup & Execution

### 1. Open a Terminal
Navigate to the project directory where these files are located:
```powershell
cd c:\gruve_projects\dev-invoice-agent
```

### 2. Build and Start the Container
Run the following command to build the Docker image and start the service in the background:
```powershell
docker compose up -d --build
```
*Wait for the process to complete. It may take a few minutes to download the base image and install dependencies.*

### 3. Verify the Service is Running
Check the status of your containers:
```powershell
docker compose ps
```
You should see `dev-invoice-agent-invoice-api` running on port `8000`.

### 4. Test the API

#### Option A: Using the provided Python script
We have included a test script `test_docker.py` that sends a sample PDF to the API.
```powershell
python test_docker.py
```

#### Option B: Using cURL
You can send a POST request with your own PDF file:
```bash
curl -X POST "http://localhost:8000/extract/invoice" ^
     -H "accept: application/json" ^
     -H "Content-Type: multipart/form-data" ^
     -F "file=@path/to/your/invoice.pdf"
```
*(Note: Replace `path/to/your/invoice.pdf` with the actual path to your file. The `^` is for PowerShell line continuation).*

### 5. Check Outputs
The service automatically saves:
- **Uploaded PDFs** in the `input_pdfs/` directory (mapped to your local folder).
- **Extracted JSONs** in the `output_json/` directory (mapped to your local folder).

## 🛑 Stopping the Service
To stop the containers:
```powershell
docker compose down
```

## Project Structure
- `main.py`: FastAPI application entry point.
- `service/invoice_ext.py`: Core logic for text and field extraction.
- `Dockerfile`: Configuration for building the application image.
- `docker-compose.yml`: Simplified startup configuration.
- `input_pdfs/`: Directory where uploaded PDFs are stored.
- `output_json/`: Directory where extracted data is saved.
