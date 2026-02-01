# Nouakchott Places Manager - Web App

A simple, beautiful web application to view and manage places data from `nouakchott_places.json`.

## Features

✨ **View all places** with ID, name, types, and location  
🔍 **Search** by name or type in real-time  
🎯 **Filter** by specific place type  
✅ **Select multiple places** for deletion  
🗑️ **Delete places** with immediate file updates  
📊 **Live statistics** showing total and selected count  
💅 **Beautiful, responsive UI** with smooth animations  

---

## Quick Start

### 1. Install Flask

```bash
pip install flask
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

### 2. Run the App

```bash
python3 app.py
```

### 3. Open in Browser

Navigate to: **http://localhost:3000**

---

## How to Use

### Viewing Places
- All 5,768 places are displayed in a scrollable table
- Each row shows: ID, Name, Types (as badges), and GPS coordinates

### Searching
- Type in the search box to filter by name or type
- Search is case-insensitive and updates in real-time

### Filtering by Type
- Use the dropdown to show only specific types (restaurant, hotel, etc.)
- Combines with search filter

### Selecting Places
- Click individual checkboxes to select places
- Use "Select All" to select all visible (filtered) places
- Use "Deselect All" to clear selection
- Click the header checkbox to toggle all visible places

### Deleting Places
1. Select one or more places using checkboxes
2. Click the "Delete Selected" button (turns red when places are selected)
3. Confirm the deletion
4. Changes are **immediately saved** to `nouakchott_places.json`

---

## Architecture

### Backend (Flask)
- **`app.py`**: Python Flask server
  - `/` - Serves the web interface
  - `/api/places` (GET) - Returns all places
  - `/api/places` (DELETE) - Deletes selected places
  - `/api/stats` - Returns statistics

### Frontend
- **`templates/index.html`**: HTML structure
- **`static/style.css`**: Modern, gradient design with animations
- **`static/script.js`**: Interactive JavaScript for filtering, selection, deletion

### Data
- **`nouakchott_places.json`**: Single source of truth
- All changes are immediately persisted to this file
- Thread-safe file operations with locks

---

## File Structure

```
famous_places_nktt/
├── app.py                      # Flask application
├── nouakchott_places.json      # Places data (modified by app)
├── templates/
│   └── index.html              # HTML template
└── static/
    ├── style.css               # Styling
    └── script.js               # Frontend logic
```

---

## Features in Detail

### Real-time Search
- Searches across place names and types
- Instant filtering without page reload
- Case-insensitive matching

### Type Filter
- Dropdown populated with all unique types from data
- 85+ different place types available
- Shows count of matching places

### Smart Selection
- Visual feedback: selected rows highlighted in blue
- Selected count updates live
- Header checkbox reflects current page state

### Safe Deletion
- Confirmation dialog before deletion
- Shows count of places to be deleted
- Success message with remaining count
- Automatic table refresh after deletion

### Performance
- Handles 5,768 places smoothly
- Client-side filtering for instant results
- Efficient rendering with vanilla JavaScript

---

## API Endpoints

### GET `/api/places`
Returns all places as JSON array.

**Response:**
```json
[
  {
    "id": 1,
    "place_id": "ChIJ...",
    "name": "Place Name",
    "types": ["restaurant", "food"],
    "latitude": 18.0735,
    "longitude": -15.9582
  }
]
```

### DELETE `/api/places`
Deletes places by ID.

**Request:**
```json
{
  "ids": [1, 2, 3]
}
```

**Response:**
```json
{
  "success": true,
  "deleted_count": 3,
  "remaining_count": 5765
}
```

### GET `/api/stats`
Returns statistics about places.

**Response:**
```json
{
  "total_places": 5768,
  "type_counts": {
    "restaurant": 450,
    "hotel": 120,
    ...
  }
}
```

---

## Security Notes

⚠️ **This is a local development tool**. Do NOT expose to the internet without:
- Adding authentication
- Validating user permissions
- Adding rate limiting
- Using HTTPS

For local use on `localhost`, it's perfectly safe.

---

## Customization

### Change Port
Edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Change 5000 to 8080
```

### Modify Colors
Edit `static/style.css`:
```css
background: linear-gradient(135deg, #your-color1 0%, #your-color2 100%);
```

### Add Features
The codebase is simple and well-commented. Easy to extend with:
- Export filtered data
- Edit place details
- Add new places
- Bulk operations

---

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5000
lsof -ti:3000 | xargs kill -9

# Or use a different port (edit app.py)
```

### Flask Not Found
```bash
pip install flask
```

### Changes Not Saving
- Check file permissions on `nouakchott_places.json`
- Make sure file is not open in another program
- Check console for error messages

### Browser Cache Issues
- Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows/Linux)
- Clear browser cache
- Try incognito/private window

---

## Tips

💡 **Backup First**: Before deleting many places, make a backup:
```bash
cp nouakchott_places.json nouakchott_places.backup.json
```

💡 **Filter Before Select All**: Use search/filter to narrow down, then "Select All" only affects visible places

💡 **Keyboard Shortcuts**: Tab to navigate, Space to check/uncheck focused checkbox

💡 **Mobile Friendly**: Responsive design works on phones and tablets

---

## Development

Running in debug mode (default):
- Auto-reloads on code changes
- Detailed error messages
- Debug toolbar available

For production:
```python
app.run(debug=False, host='0.0.0.0', port=3000)
```

---

## Data Integrity

✅ **Thread-safe**: File locks prevent concurrent write issues  
✅ **Atomic writes**: File is fully written or not at all  
✅ **Validation**: IDs validated before deletion  
✅ **Preserves format**: JSON stays pretty-printed and UTF-8 encoded  

---

Enjoy managing your Nouakchott places data! 🎉
