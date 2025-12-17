#import necessary libraries
import json
import os
from pathlib import Path
import pandas as pd

#Define function to transform NASA data
def transform_nasa_data():
    project_root = Path(__file__).resolve().parents[1]
    raw_path = project_root / "data" / "raw" / "nasa_data.json"
    staged_dir = project_root / "data" / "staged"
    staged_dir.mkdir(parents=True, exist_ok=True)
    
    if not raw_path.exists():
        raise FileNotFoundError(f"{raw_path} does not exist. Run extract step first.")
    
    with raw_path.open("r") as f:
        data = json.load(f)
    
    # Handle both single object and list of objects
    if isinstance(data, dict):
        data = [data]
    
    # Extract relevant fields from all records
    records = []
    for record in data:
        records.append({
            "date": record.get('date'),
            "title": record.get("title"),
            "explanation": record.get('explanation'),
            "media_type": record.get('media_type', 'image'),
            "image_url": record.get("url") or record.get("thumbnail_url")  # Use thumbnail for videos
        })
    
    df = pd.DataFrame(records)
    
    output_path = staged_dir / "nasa_data_staged.csv"
    df.to_csv(output_path, index=False)
    
    print(f"Transformed {len(df)} NASA records saved to {output_path}")
    return df

if __name__=="__main__":
    transform_nasa_data()