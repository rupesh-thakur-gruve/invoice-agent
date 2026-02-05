from fastapi import FastAPI

from core.logger import setup_logger
from router.invoice_router import router as invoice_router

# Setup logger
logger = setup_logger(__name__)

app = FastAPI()

# Include the invoice router
app.include_router(invoice_router, prefix="/extract")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Invoice Extraction API...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Invoice Extraction API...")

@app.get("/")
def read_root():
    logger.info("Health check endpoint called.")
    return {"status": "Invoice Extraction API is running"}
