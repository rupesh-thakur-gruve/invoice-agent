try:
    import fitz
    print("PyMuPDF (fitz) imported successfully.")
    print(fitz.__doc__)
except ImportError as e:
    print(f"Failed to import PyMuPDF: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
