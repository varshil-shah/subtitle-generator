from waitress import serve
from app import app
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    print(f"Starting Waitress server on port {port}...")
    serve(
        app,
        host='0.0.0.0',
        port=port,
        threads=4,
        channel_timeout=900
    )
