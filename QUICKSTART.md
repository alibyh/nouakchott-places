# Quick Start Guide

⚡ **Fast track to extracting places in Nouakchott**

## 1️⃣ Install (30 seconds)

```bash
pip install googlemaps
```

## 2️⃣ Get API Key (2 minutes)

1. Go to: https://console.cloud.google.com/
2. Create/select project
3. Enable **Places API**
4. Create API key
5. Enable billing (has free tier)

## 3️⃣ Set API Key (10 seconds)

```bash
export GOOGLE_PLACES_API_KEY='your-key-here'
```

## 4️⃣ Test (30 seconds)

```bash
python3 test_setup.py
```

Should see: ✅ Setup is correct!

## 5️⃣ Run Extraction (1-2 hours)

```bash
python3 extract_places.py
```

## 6️⃣ Check Output

```bash
# Count places
jq '. | length' nouakchott_places.json

# View sample
jq '.[0:5]' nouakchott_places.json
```

---

## Expected Results

| Config | Time | Cost | Places |
|--------|------|------|--------|
| Default (10×10) | ~2h | ~$120 | 2-4k |
| Small (5×5) | ~20m | ~$30 | 1-2k |
| Large (15×15) | ~4h | ~$300 | 3-6k |

---

## Common Issues

### ❌ "REQUEST_DENIED"
→ Enable Places API in console + Enable billing

### ❌ "OVER_QUERY_LIMIT"
→ Exceeded quota, wait or increase limit

### ⚠️ Taking too long?
→ Reduce grid in config: `GRID_LAT_DIVISIONS = 5`

### ⚠️ Interrupted?
→ Just run again, it auto-resumes from checkpoint

---

## Files Generated

- `nouakchott_places.json` - Final output
- `extraction.log` - Progress log
- `extraction_checkpoint.json` - Resume file (auto-deleted on finish)

---

## Customization

Edit `extract_places.py` top section:

```python
class Config:
    # Change these
    GRID_LAT_DIVISIONS: int = 10  # More = more coverage
    PLACE_TYPES: List[str] = [...]  # Add/remove types
    SEARCH_RADIUS_METERS: int = 1000  # Adjust coverage
```

See `CONFIGURATION.md` for details.

---

## Output Format

```json
[
  {
    "place_id": "ChIJxxxx",
    "name": "Restaurant Name",
    "types": ["restaurant", "food"],
    "latitude": 18.0735,
    "longitude": -15.9582
  }
]
```

---

## Need Help?

1. Check `extraction.log` for errors
2. Read `README.md` for details
3. Run `test_setup.py` to diagnose issues

---

**Ready? Let's go!**

```bash
python3 extract_places.py
```
