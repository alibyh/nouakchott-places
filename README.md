# Google Places Extractor - Nouakchott, Mauritania

## Overview

This script systematically extracts **maximum achievable coverage** of Google Maps places in Nouakchott, Mauritania using the official Google Places API.

## Why This Approach?

The Google Places API does **not** provide a "list all places in a city" endpoint. A naive single query would return only ~60 results (the API's hard pagination limit), missing thousands of actual places.

### The Problem

- **Result Truncation**: Each query returns max 60 results (3 pages × 20), ranked by Google's prominence algorithm
- **No Comprehensive Endpoint**: No way to request "all places" directly
- **Ranking Bias**: Google prioritizes certain places; most businesses remain hidden in single queries

### The Solution

**Grid-based Exhaustive Search + Type Iteration**:

1. **Geographic Grid**: Divide Nouakchott into 100+ small cells
2. **Type Exhaustion**: Query each cell with 60+ different place types
3. **Multiplication Effect**: N cells × M types × 60 results = comprehensive coverage
4. **Deduplication**: Use `place_id` to eliminate duplicates across queries

This maximizes coverage while respecting API constraints.

## Features

✅ **Grid-based city coverage** - No blind spots  
✅ **60+ place type categories** - Restaurants, hotels, services, retail, etc.  
✅ **Full pagination handling** - All 3 pages per query  
✅ **Deduplication** - Unique `place_id` tracking  
✅ **Exponential backoff** - Robust error handling  
✅ **Resume capability** - Checkpoint system for interruptions  
✅ **Progress logging** - Real-time statistics  
✅ **Configurable** - All parameters centralized  

## Requirements

- Python 3.7+
- Google Places API key with Places API enabled
- Sufficient API quota (script may make 5,000-10,000+ requests)

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API key
export GOOGLE_PLACES_API_KEY='your-api-key-here'
```

## Usage

### Basic Usage

```bash
python extract_places.py
```

### Configuration

All configuration is in the `Config` class at the top of the script:

```python
@dataclass
class Config:
    # API Key (or use environment variable)
    API_KEY: str = os.getenv("GOOGLE_PLACES_API_KEY", "YOUR_API_KEY_HERE")
    
    # Bounding box for Nouakchott
    BBOX_NORTH: float = 18.15
    BBOX_SOUTH: float = 17.95
    BBOX_EAST: float = -15.85
    BBOX_WEST: float = -16.10
    
    # Grid resolution (10×10 = 100 cells)
    GRID_LAT_DIVISIONS: int = 10
    GRID_LNG_DIVISIONS: int = 10
    
    # Search radius per cell
    SEARCH_RADIUS_METERS: int = 1000
    
    # Rate limiting
    DELAY_BETWEEN_REQUESTS_SECONDS: float = 0.5
    
    # Output file
    OUTPUT_FILE: str = "nouakchott_places.json"
```

### Adjusting Coverage vs. API Quota

**Higher Coverage** (more API calls):
- Increase `GRID_LAT_DIVISIONS` and `GRID_LNG_DIVISIONS` (e.g., 15×15 = 225 cells)
- Add more place types to `PLACE_TYPES` list
- Decrease `SEARCH_RADIUS_METERS` (smaller radius = less overlap)

**Lower API Usage** (faster, fewer calls):
- Decrease grid divisions (e.g., 5×5 = 25 cells)
- Remove uncommon place types from list
- Increase radius (larger coverage per query)

**Expected API Calls**:
```
Calls = (Grid Cells × Place Types × Pages per Query)
      = (100 cells × 65 types × ~1.5 pages avg)
      ≈ 9,750 requests
```

## Output Format

The script generates `nouakchott_places.json` with this exact schema:

```json
[
  {
    "place_id": "ChIJxxxxxxxxxxxxx",
    "name": "Restaurant Example",
    "types": ["restaurant", "food", "point_of_interest"],
    "latitude": 18.0735,
    "longitude": -15.9582
  }
]
```

- **UTF-8 encoded**
- **Pretty-printed** (2-space indent)
- **Sorted alphabetically** by name
- **No duplicates** (by `place_id`)

## Resume Capability

If the script is interrupted (Ctrl+C, error, rate limit), it automatically saves a checkpoint:

```bash
# First run (interrupted)
python extract_places.py
# ... processes 50/100 cells ...
# ^C (user interrupts)

# Resume from checkpoint
python extract_places.py
# Automatically continues from cell 51
```

Checkpoint file: `extraction_checkpoint.json` (auto-deleted on completion)

## Logging

The script creates `extraction.log` with detailed progress:

```
2026-02-01 10:15:23 - INFO - Starting extraction from cell 0/100
2026-02-01 10:15:25 - INFO - Cell 1/100 - Row 0, Col 0 - Center: (17.9600, -16.0875)
2026-02-01 10:15:27 - INFO -   Type 1/65: restaurant (unique places so far: 12)
2026-02-01 10:15:30 - INFO -   Type 2/65: cafe (unique places so far: 18)
...
2026-02-01 14:32:15 - INFO - Cell 100 complete. Total unique: 2,847, Duplicates skipped: 1,523
2026-02-01 14:32:16 - INFO - SUCCESS: Extraction finished successfully!
```

## Known Limitations

These are **inherent to the Google Places API**, not bugs:

1. **Hidden Places**: Some businesses may not be listed in Google's database
2. **API Ranking**: Google's algorithms determine visibility; we cannot override
3. **Rate Limits**: Free tier = 100,000 requests/month
4. **New Listings**: Recently added places may not appear immediately
5. **Coverage Gaps**: Despite systematic approach, 100% coverage is impossible

## Troubleshooting

### "API Key Invalid"
- Ensure Places API is enabled in Google Cloud Console
- Check billing is enabled (API requires billing even for free tier)
- Verify key is correct: `echo $GOOGLE_PLACES_API_KEY`

### "Quota Exceeded"
- Check quota in Google Cloud Console
- Reduce grid divisions or place types
- Wait for quota reset (daily/monthly)

### "Too Many Duplicates"
- This is normal! It means the grid+type strategy is working
- Duplicates show overlap between queries (desired behavior)
- Only unique places are saved to output

### Script Running for Hours
- **This is expected** for comprehensive coverage
- 10,000 requests × 0.5s delay = ~1.5 hours minimum
- Use checkpoints to pause/resume as needed

## Performance Estimates

| Grid Size | Place Types | Est. Requests | Est. Time | Expected Places |
|-----------|-------------|---------------|-----------|-----------------|
| 5×5 (25)  | 65          | ~2,500        | 20 min    | 800-1,500       |
| 10×10 (100) | 65        | ~10,000       | 90 min    | 2,000-4,000     |
| 15×15 (225) | 65        | ~22,500       | 3 hours   | 3,000-6,000     |

*Actual results depend on place density and API response patterns.*

## Cost Estimation

Google Places API Pricing (as of 2026):
- **Nearby Search**: $32 per 1,000 requests
- **Free tier**: $200/month credit = ~6,250 free requests/month

**Example**:
- 10,000 requests = $320 - $200 (credit) = **$120 actual cost**
- Adjust grid/types to stay within free tier if needed

## Advanced Usage

### Custom Bounding Box

To extract a different city, update the bounding box:

```python
# Example: Different area
BBOX_NORTH: float = 18.20
BBOX_SOUTH: float = 18.00
BBOX_EAST: float = -15.80
BBOX_WEST: float = -16.00
```

### Custom Place Types

Add specific categories you care about:

```python
PLACE_TYPES: List[str] = [
    "restaurant",
    "hotel",
    "atm",
    # ... your types ...
]
```

### Parallel Execution

For faster extraction (if you have high quota), run multiple instances with different grid sections:

```python
# Instance 1: Rows 0-4
# Instance 2: Rows 5-9
# Then merge the JSON files
```

## Data Engineering Considerations

This script is designed for **production data extraction**:

- ✅ Idempotent (can re-run safely)
- ✅ Resumable (checkpoints)
- ✅ Observable (detailed logging)
- ✅ Fault-tolerant (retry logic)
- ✅ Configurable (no hardcoded values)
- ✅ Validated output schema

## License

MIT License - Use freely for any purpose.

## Support

For issues:
1. Check `extraction.log` for detailed error messages
2. Verify API key and quota in Google Cloud Console
3. Test with smaller grid (5×5) first
4. Review Known Limitations section

---

**Built for data engineering workloads. Designed to run for hours and handle millions of data points reliably.**
