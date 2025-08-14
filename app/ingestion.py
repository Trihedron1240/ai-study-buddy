# app/ingestion.py
import time

def fetch_and_process_data(source_url: str):
    """Fetches data, processes it, and stores it."""
    print(f"[Worker] Starting ingestion for: {source_url}")
    
    # Simulate download
    time.sleep(2)
    print(f"[Worker] Downloaded data from {source_url}")

    # Simulate processing
    processed_data = source_url.upper()  # Example transformation
    time.sleep(1)
    print(f"[Worker] Processed data: {processed_data}")

    # In a real app, you’d save this to your DB
    return {"source": source_url, "processed": processed_data}
