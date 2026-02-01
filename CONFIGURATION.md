# Configuration Guide

This document explains all configuration options in detail to help you optimize the extraction for your specific needs.

## Configuration Parameters

All parameters are in the `Config` dataclass at the top of `extract_places.py`.

---

## 1. API Configuration

### `API_KEY`
- **Type**: `str`
- **Default**: Reads from `GOOGLE_PLACES_API_KEY` environment variable
- **Description**: Your Google Places API key
- **How to get**:
  1. Go to [Google Cloud Console](https://console.cloud.google.com/)
  2. Create a project (or use existing)
  3. Enable "Places API"
  4. Create credentials (API key)
  5. Enable billing (required even for free tier)

**Recommended**: Use environment variable for security
```bash
export GOOGLE_PLACES_API_KEY='AIza...'
```

---

## 2. Geographic Coverage

### `BBOX_NORTH`, `BBOX_SOUTH`, `BBOX_EAST`, `BBOX_WEST`
- **Type**: `float` (decimal degrees)
- **Defaults**: Cover Nouakchott metropolitan area
  - North: 18.15°
  - South: 17.95°
  - East: -15.85°
  - West: -16.10°

**How to customize**:
1. Open [Google Maps](https://www.google.com/maps)
2. Right-click on the north boundary of your area → Click coordinates to copy
3. Repeat for south, east, west boundaries
4. Update the config values

**Example for a different city**:
```python
# Dakar, Senegal (example)
BBOX_NORTH: float = 14.78
BBOX_SOUTH: float = 14.65
BBOX_EAST: float = -17.40
BBOX_WEST: float = -17.50
```

**Important**: Ensure the box fully covers your target area with some margin.

---

## 3. Grid Configuration

### `GRID_LAT_DIVISIONS`
- **Type**: `int`
- **Default**: `10`
- **Description**: Number of rows in the grid
- **Impact**: 
  - Higher = More coverage, more API calls
  - Lower = Faster, but may miss places

### `GRID_LNG_DIVISIONS`
- **Type**: `int`
- **Default**: `10`
- **Description**: Number of columns in the grid
- **Impact**: Same as lat divisions

**Total cells = `GRID_LAT_DIVISIONS × GRID_LNG_DIVISIONS`**

**Guidelines**:
- **Small city or testing**: 5×5 (25 cells)
- **Medium city**: 10×10 (100 cells) ← Default
- **Large city or maximum coverage**: 15×15 (225 cells)
- **Very dense urban area**: 20×20 (400 cells)

**Calculate your cell size**:
```
Cell width (km) = (BBOX_EAST - BBOX_WEST) × 111.32 / GRID_LNG_DIVISIONS
Cell height (km) = (BBOX_NORTH - BBOX_SOUTH) × 111.32 / GRID_LAT_DIVISIONS
```

For Nouakchott (10×10):
- Each cell is ~2.5km × 2.2km

**Recommendation**: Start with 10×10, then increase if results show gaps.

---

## 4. Search Parameters

### `SEARCH_RADIUS_METERS`
- **Type**: `int`
- **Default**: `1000` (1km)
- **Range**: 1 to 50,000 meters
- **Description**: Search radius around each grid cell center

**Trade-offs**:
- **Smaller radius** (500m):
  - ✅ Less likely to hit 60-result cap
  - ✅ More precise coverage
  - ❌ May create coverage gaps between cells
  
- **Larger radius** (2000m):
  - ✅ Ensures overlapping coverage (no gaps)
  - ❌ More likely to hit result truncation
  - ❌ More duplicates

**Recommendation**: 
- Radius should be ≥ half of your cell diagonal
- For 10×10 grid over Nouakchott: 1000-1500m is optimal

**Formula**:
```
Minimum safe radius = sqrt(cell_width² + cell_height²) / 2
```

---

## 5. Place Types

### `PLACE_TYPES`
- **Type**: `List[str]`
- **Default**: 60+ common types
- **Description**: List of place categories to query

**Current categories**:
- Food & Drink: restaurant, cafe, bar, bakery
- Accommodation: hotel, lodging
- Services: pharmacy, hospital, bank, salon
- Retail: store, supermarket, mall
- Transport: gas_station, bus_station, airport
- ... and 50+ more

**Customization strategies**:

**Reduce API calls** (keep only essential):
```python
PLACE_TYPES: List[str] = [
    "restaurant", "hotel", "bank", "hospital",
    "supermarket", "gas_station", "school", "mosque"
]
```

**Maximize coverage** (add more niche types):
```python
PLACE_TYPES: List[str] = [
    # ... existing types ...
    "bicycle_store", "bowling_alley", "car_wash",
    "book_store", "convenience_store", "electronics_store",
    # ... add any type from Google's list
]
```

**Full list of Google place types**:
https://developers.google.com/maps/documentation/places/web-service/supported_types

### `INCLUDE_GENERIC_SEARCH`
- **Type**: `bool`
- **Default**: `True`
- **Description**: Also perform searches without type filter

**Recommendation**: Keep `True` to catch places that don't fit standard categories.

---

## 6. Rate Limiting & Retry

### `DELAY_BETWEEN_REQUESTS_SECONDS`
- **Type**: `float`
- **Default**: `0.5` (500ms)
- **Description**: Wait time between API requests

**Guidelines**:
- **Standard quota**: 0.5s (120 requests/minute)
- **Higher quota**: 0.1s (600 requests/minute)
- **Conservative**: 1.0s (60 requests/minute)

**Avoid going below 0.1s** to prevent rate limit errors.

### `PAGINATION_DELAY_SECONDS`
- **Type**: `float`
- **Default**: `2.5`
- **Description**: Wait before using `next_page_token`

**Important**: Google requires ~2 seconds for the token to become valid. Don't reduce below 2.0s.

### `MAX_RETRIES`
- **Type**: `int`
- **Default**: `5`
- **Description**: Max retry attempts on API errors

**Recommendation**: 5 is robust. Increase to 10 if you have unstable internet.

### `INITIAL_RETRY_DELAY_SECONDS`
- **Type**: `float`
- **Default**: `1.0`
- **Description**: First retry delay (doubles each retry)

**Exponential backoff sequence**: 1s → 2s → 4s → 8s → 16s

---

## 7. Output Configuration

### `OUTPUT_FILE`
- **Type**: `str`
- **Default**: `"nouakchott_places.json"`
- **Description**: Final output filename

**Examples**:
```python
OUTPUT_FILE: str = "nouakchott_places_2026-02-01.json"  # Timestamped
OUTPUT_FILE: str = "data/places.json"  # In subdirectory
OUTPUT_FILE: str = "nouakchott_complete.json"  # Custom name
```

### `CHECKPOINT_FILE`
- **Type**: `str`
- **Default**: `"extraction_checkpoint.json"`
- **Description**: Resume checkpoint filename

### `LOG_FILE`
- **Type**: `str`
- **Default**: `"extraction.log"`
- **Description**: Progress log filename

---

## 8. Checkpointing

### `ENABLE_CHECKPOINTING`
- **Type**: `bool`
- **Default**: `True`
- **Description**: Enable resume capability

**Recommendation**: Keep `True` for long-running extractions.

### `CHECKPOINT_INTERVAL`
- **Type**: `int`
- **Default**: `10`
- **Description**: Save checkpoint every N cells

**Guidelines**:
- **Frequent checkpoints** (5): Resume with less re-work, but slower
- **Standard** (10): Good balance ← Default
- **Infrequent** (25): Faster, but lose more progress on interrupt

---

## Optimization Scenarios

### Scenario 1: Testing / Development
**Goal**: Fast iteration, low cost

```python
GRID_LAT_DIVISIONS: int = 3
GRID_LNG_DIVISIONS: int = 3
SEARCH_RADIUS_METERS: int = 2000
PLACE_TYPES: List[str] = ["restaurant", "hotel", "bank"]
DELAY_BETWEEN_REQUESTS_SECONDS: float = 0.5
```

**Result**: ~50 requests, 2-3 minutes, $0.02

---

### Scenario 2: Production - Balanced
**Goal**: Good coverage, reasonable cost

```python
GRID_LAT_DIVISIONS: int = 10
GRID_LNG_DIVISIONS: int = 10
SEARCH_RADIUS_METERS: int = 1000
PLACE_TYPES: List[str] = [all 60+ default types]
DELAY_BETWEEN_REQUESTS_SECONDS: float = 0.5
```

**Result**: ~10,000 requests, 90 minutes, $120

---

### Scenario 3: Maximum Coverage
**Goal**: Extract everything possible, cost is not a concern

```python
GRID_LAT_DIVISIONS: int = 20
GRID_LNG_DIVISIONS: int = 20
SEARCH_RADIUS_METERS: int = 800
PLACE_TYPES: List[str] = [all 100+ types from Google's list]
DELAY_BETWEEN_REQUESTS_SECONDS: float = 0.2
```

**Result**: ~50,000 requests, 4-6 hours, $600+

---

### Scenario 4: Free Tier Only
**Goal**: Stay within $200 credit

```python
GRID_LAT_DIVISIONS: int = 7
GRID_LNG_DIVISIONS: int = 7
SEARCH_RADIUS_METERS: int = 1500
PLACE_TYPES: List[str] = [20-25 most important types]
DELAY_BETWEEN_REQUESTS_SECONDS: float = 0.5
```

**Result**: ~2,500 requests, 30 minutes, $80 (within free tier)

---

## Monitoring & Tuning

### During Extraction

Watch `extraction.log` for:
1. **Duplicates ratio**: High duplicates = good overlap (desired)
2. **Results per query**: If often hitting 60 = need smaller radius or more cells
3. **Zero results**: If many = radius too small or cell too sparse

### After Extraction

Analyze output:
```bash
# Count total places
jq '. | length' nouakchott_places.json

# Places by type
jq '[.[].types[0]] | group_by(.) | map({type: .[0], count: length})' nouakchott_places.json

# Geographic distribution
jq 'group_by(.latitude | floor) | map({lat: .[0].latitude | floor, count: length})' nouakchott_places.json
```

### Adjust if:
- **Too few results**: Increase grid divisions, add more types
- **Many duplicates**: Expected! Means good overlap
- **Uneven distribution**: Check if bounding box covers entire area
- **Specific types missing**: Add those types to `PLACE_TYPES`

---

## Performance Formulas

### Estimated API Calls
```
Total Calls = Cells × (Types + Generic) × Avg Pages Per Query
           = (LAT_DIV × LNG_DIV) × (len(PLACE_TYPES) + 1) × 1.3

Default: (10 × 10) × (60 + 1) × 1.3 ≈ 7,930 calls
```

### Estimated Time
```
Time = Total Calls × (Delay + Avg Response Time)
     = 7,930 × (0.5s + 0.3s)
     = ~106 minutes

With pagination delays: +20-30 minutes
Total: ~2 hours
```

### Estimated Cost
```
Cost = (Total Calls / 1000) × $32 - $200 (free credit)
     = (7,930 / 1000) × $32 - $200
     = $253.76 - $200
     = $53.76 actual cost
```

---

## Best Practices

1. **Start small**: Test with 5×5 grid first
2. **Monitor logs**: Watch for patterns and errors
3. **Use checkpoints**: Don't disable for long runs
4. **Verify output**: Check a sample of places in Google Maps
5. **Document changes**: Note your config in git commits
6. **Respect quotas**: Don't set delay below 0.1s
7. **Plan for cost**: Calculate before running at scale

---

## Troubleshooting Configuration

### "Not enough results"
→ Increase `GRID_LAT_DIVISIONS` and `GRID_LNG_DIVISIONS`

### "Taking too long"
→ Decrease grid divisions, reduce `PLACE_TYPES` list

### "Rate limit errors"
→ Increase `DELAY_BETWEEN_REQUESTS_SECONDS`

### "Many zero-result queries"
→ Increase `SEARCH_RADIUS_METERS`

### "Hitting 60-result cap frequently"
→ Decrease `SEARCH_RADIUS_METERS`, increase grid divisions

### "Coverage gaps in map"
→ Ensure `SEARCH_RADIUS_METERS` ≥ (cell diagonal / 2)

---

For more help, see README.md or check extraction.log for specific errors.
