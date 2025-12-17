# ETL_NASA

## Overview

ETL_NASA is a production-ready **Extract-Transform-Load (ETL)** pipeline that automates the collection, processing, and storage of NASA's Astronomy Picture of the Day (APOD) data. This project demonstrates industry best practices for data engineering, API integration, and cloud database management.

### Key Features

- **Multi-Day Data Extraction**: Fetches NASA APOD data for multiple days to ensure comprehensive data collection
- **Real-Time Data Processing**: Transforms raw API responses into structured, analyzable formats
- **Cloud Database Integration**: Loads processed data into Supabase (PostgreSQL-based)
- **Automated Pipeline**: Modular, reusable scripts for seamless data orchestration
- **Environment Configuration**: Secure credential management using `.env` files
- **Scalable Architecture**: Batch processing with configurable intervals
- **On-Conflict Handling**: Duplicate detection and update mechanism for data integrity

---

## Project Structure

```
ETL_NASA/
├── scripts/               # ETL pipeline modules
│   ├── extract-1.py          # Extract NASA APOD data for multiple days
│   ├── transform-1.py        # Clean and structure APOD data
│   └── load-1.py            # Load data to Supabase database
├── data/                  # Data storage
│   ├── raw/                   # Raw JSON responses from NASA API
│   └── staged/                # Cleaned and transformed data (CSV)
├── .env                   # Environment variables (credentials)
└── README.md              # Project documentation
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.x |
| **API** | NASA APOD API |
| **Data Processing** | Pandas, JSON |
| **Database** | Supabase (PostgreSQL) |
| **Libraries** | requests, python-dotenv, pathlib |
| **Error Handling** | PostgreSQL conflict resolution |

---

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Supabase account and credentials
- NASA API key (free from [NASA API](https://api.nasa.gov/))

### Step 1: Clone the Repository

```bash
git clone https://github.com/Abhinav7301/ETL_NASA.git
cd ETL_NASA
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
```
pandas>=1.3.0
requests>=2.26.0
python-dotenv>=0.19.0
supabase>=1.0.0
```

### Step 4: Configure Environment Variables

Create a `.env` file in the root directory:

```env
API_KEY=your_nasa_api_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key_here
```

**Obtaining Credentials:**
- **NASA API Key**: Register at [https://api.nasa.gov/](https://api.nasa.gov/)
- **Supabase Credentials**: Create a project at [https://supabase.com](https://supabase.com)

---

## Pipeline Workflow

### 1. **Extract Phase**

#### `extract-1.py`
Fetches NASA Astronomy Picture of the Day (APOD) data for multiple days and saves as JSON.

**Key Functions:**
```python
extract_nasa_data(api_key=NASA_KEY, days_back=8)
```

**Parameters:**
- `api_key` (str): NASA API key (from environment variables)
- `days_back` (int): Number of days to fetch (default: 8 days)

**Process:**
1. Calculates date range (current date - N days)
2. Queries NASA APOD API with start and end dates
3. Retrieves thumbnail URLs for videos (converts to viewable content)
4. Saves JSON response to `/data/raw/nasadata.json`
5. Handles API rate limits and connection errors

```bash
python scripts/extract-1.py
```

**Output**: `data/raw/nasadata.json`

**Sample Response:**
```json
{
  "copyright": "Bugin",
  "date": "2025-12-09",
  "explanation": "This cosmic close-up looks deep inside the Soul Nebula...",
  "hdurl": "https://apod.nasa.gov/apod/image/2512/SoulBugin3710.jpg",
  "mediatype": "image",
  "serviceversion": "v1",
  "title": "The Heart of the Soul Nebula",
  "url": "https://apod.nasa.gov/apod/image/2512/SoulBugin1080.jpg"
}
```

### 2. **Transform Phase**

#### `transform-1.py`
Cleans and structures NASA APOD JSON data into CSV format.

**Key Functions:**
```python
transform_nasa_data()
```

**Transformations:**
- Extracts relevant fields from NASA API response
- Handles both single objects and list of objects
- Converts timestamps to standardized ISO format
- Renames fields for clarity
- Manages missing values and URL fallbacks
- Handles video content (uses thumbnail URLs)

```bash
python scripts/transform-1.py
```

**Output**: `data/staged/nasadata.csv`

**Sample Output (CSV):**
```csv
date,title,explanation,mediatype,imageurl
2025-12-09,The Heart of the Soul Nebula,This cosmic close-up looks deep inside the Soul Nebula...,image,https://apod.nasa.gov/apod/image/2512/SoulBugin1080.jpg
2025-12-08,Aurora at the Edge,An unexpected appearance...,image,https://apod.nasa.gov/apod/image/2512/Aurora2025.jpg
```

### 3. **Load Phase**

#### `load-1.py`
Loads cleaned data into Supabase database with batch processing and conflict resolution.

**Key Features:**
- Batch insert (default: 20 records per batch)
- Automatic timestamp conversion to ISO format
- NULL value handling
- On-conflict update mechanism (prevents duplicate errors)
- Rate limiting (0.5s between batches)
- Direct SQL execution via Supabase RPC

**Key Functions:**
```python
load_to_supabase()
```

```bash
python scripts/load-1.py
```

**Database Table Schema:**
```sql
CREATE TABLE nasa_apod (
    id BIGSERIAL PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    title VARCHAR(500),
    explanation TEXT,
    mediatype VARCHAR(50),
    imageurl VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON CONFLICT (date) DO UPDATE 
      SET title = EXCLUDED.title, 
          explanation = EXCLUDED.explanation, 
          mediatype = EXCLUDED.mediatype, 
          imageurl = EXCLUDED.imageurl,
          updated_at = CURRENT_TIMESTAMP
);
```

**Insert Statement:**
```sql
INSERT INTO nasa_apod (date, title, explanation, mediatype, imageurl) 
VALUES ('2025-12-09', 'Title', 'Explanation', 'image', 'URL')
ON CONFLICT (date) DO UPDATE 
SET title = EXCLUDED.title, 
    explanation = EXCLUDED.explanation, 
    mediatype = EXCLUDED.mediatype, 
    imageurl = EXCLUDED.imageurl
```

---

## Usage Examples

### Run Complete ETL Pipeline

```bash
# Extract NASA APOD data for last 8 days
python scripts/extract-1.py

# Transform raw JSON to CSV
python scripts/transform-1.py

# Load to Supabase database
python scripts/load-1.py
```

### Custom Extraction (Different Number of Days)

Modify `extract-1.py`:

```python
extract_nasa_data(api_key=NASA_KEY, days_back=30)  # Fetch 30 days of data
```

### Error Handling

The pipeline includes robust error handling:

```python
try:
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
except requests.RequestException as e:
    print(f"API request failed: {e}")
except APIError as e:
    print(f"Database error: {e}")
```

---

## Configuration

### Extract Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | str | NASA_KEY env var | NASA APOD API key |
| `days_back` | int | 8 | Number of days to fetch |
| `thumbs` | bool | True | Include thumbnail URLs for videos |
| `timeout` | int | 15 | API request timeout (seconds) |

### Batch Processing Settings

Edit `load-1.py` to adjust:

```python
batch_size = 20  # Records per batch (adjust as needed)
time.sleep(0.5)  # Delay between batches (seconds)
```

### API Rate Limits

- **NASA APOD API**: 1000 requests per hour per IP
- **Supabase**: Depends on your plan

---

## Error Handling

### Common Issues & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError: Missing file` | Missing data file | Run extract and transform steps |
| `ConnectionError: Failed to fetch API` | Network/API issue | Check internet connection and API credentials |
| `Invalid SUPABASE_URL` | Missing environment variable | Verify `.env` configuration |
| `UNIQUE constraint violation` | Duplicate data | Database uses ON CONFLICT, should auto-update |
| `API rate limit exceeded` | Too many requests | Implement backoff strategy or increase time delays |

---

## Performance & Optimization

- **Batch Processing**: Reduces database load with 20-record batches
- **Rate Limiting**: 0.5s delay between batches prevents server overload
- **Memory Efficiency**: Processes data without loading entire datasets into memory
- **Scalability**: Architecture supports hourly/daily automated runs via cron jobs
- **On-Conflict Resolution**: Prevents duplicate insertion errors

---

## Security Considerations

1. **Never commit `.env` file** to version control
2. **Use Supabase RLS (Row Level Security)** for production
3. **Rotate API keys** periodically
4. **Encrypt sensitive data** in transit (HTTPS/TLS)
5. **Monitor logs** for unauthorized access attempts
6. **Validate API responses** before processing

---

## Deployment

### Deploy to Cloud (Example: Heroku)

```bash
# Create Procfile
echo "worker: python scripts/load-1.py" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

### Schedule with GitHub Actions

Create `.github/workflows/etl-schedule.yml`:

```yaml
name: ETL_NASA Pipeline
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
jobs:
  etl:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run ETL
        env:
          API_KEY: ${{ secrets.API_KEY }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: |
          pip install -r requirements.txt
          python scripts/extract-1.py
          python scripts/transform-1.py
          python scripts/load-1.py
```

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the **MIT License** - see the LICENSE file for details.

---

## Contact & Support

- **Author**: Abhinav7301
- **GitHub**: [Abhinav7301/ETL_NASA](https://github.com/Abhinav7301/ETL_NASA)
- **Issues**: [Report a bug](https://github.com/Abhinav7301/ETL_NASA/issues)
- **Discussions**: [Start a discussion](https://github.com/Abhinav7301/ETL_NASA/discussions)

---

## Acknowledgments

- [NASA APOD API](https://api.nasa.gov/) - Astronomy Picture of the Day
- [Supabase](https://supabase.com/) - PostgreSQL platform
- [Pandas](https://pandas.pydata.org/) - Data manipulation library
- [Requests](https://requests.readthedocs.io/) - HTTP library

---

## Data Source Information

**NASA Astronomy Picture of the Day (APOD)**
- **URL**: https://api.nasa.gov/
- **Updated**: Daily at ~10 PM Eastern Time
- **Coverage**: Extends back to 1995
- **Content**: High-resolution astronomical images with scientific explanations

---

**Last Updated**: December 2025
**Version**: 1.0.0
