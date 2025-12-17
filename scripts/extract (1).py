#import necessary libraries
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta

#set up data directory and path
DATA_DIR = Path(__file__).resolve().parents[1]/"data"/"raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv()
nasa_key = os.getenv("api_key") or os.getenv("NASA_API_KEY")

#define function to extract weather data
def extract_nasa_data(api_key=nasa_key, days_back=8):
    """
    Fetch APOD data for the last N days.
    
    Args:
        api_key: NASA API key
        days_back: Number of days to fetch (default: 8, to ensure we get latest published data)
    """
    if not api_key:
        raise ValueError("NASA API key is missing. Set env var 'api_key' or 'NASA_API_KEY'.")

    url = "https://api.nasa.gov/planetary/apod"
    
    # Calculate date range: fetch last 8 days of data
    # (NASA publishes around 10 PM ET daily, so we fetch extra day to ensure latest)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days_back)
    
    params = {
        "api_key": api_key,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "thumbs": True  # Get thumbnail URL for videos
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    
    # Ensure data is always a list
    if isinstance(data, dict):
        data = [data]

    filename = DATA_DIR/f"nasa_data.json"
    filename.write_text(json.dumps(data, indent = 2))

    print(f"Fetched {len(data)} APOD records from {start_date} to {end_date}")
    print(f"NASA data saved to {filename}")
    return data

if __name__ == "__main__":
    extract_nasa_data()