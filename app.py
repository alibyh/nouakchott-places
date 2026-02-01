#!/usr/bin/env python3
"""
Web app for managing Nouakchott places data.
Provides a simple interface to view and delete places.
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from threading import Lock

app = Flask(__name__)

# File path for the places data
PLACES_FILE = 'nouakchott_places.json'

# Thread lock for file operations
file_lock = Lock()


def load_places():
    """Load places from JSON file."""
    with file_lock:
        if os.path.exists(PLACES_FILE):
            with open(PLACES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []


def save_places(places):
    """Save places to JSON file."""
    with file_lock:
        with open(PLACES_FILE, 'w', encoding='utf-8') as f:
            json.dump(places, f, ensure_ascii=False, indent=2)


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/places', methods=['GET'])
def get_places():
    """Get all places."""
    places = load_places()
    return jsonify(places)


@app.route('/api/places', methods=['DELETE'])
def delete_places():
    """Delete selected places by IDs."""
    data = request.get_json()
    ids_to_delete = set(data.get('ids', []))
    
    if not ids_to_delete:
        return jsonify({'error': 'No IDs provided'}), 400
    
    # Load current places
    places = load_places()
    
    # Filter out the places to delete
    remaining_places = [p for p in places if p['id'] not in ids_to_delete]
    
    # Save the updated list
    save_places(remaining_places)
    
    deleted_count = len(places) - len(remaining_places)
    
    return jsonify({
        'success': True,
        'deleted_count': deleted_count,
        'remaining_count': len(remaining_places)
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about the places."""
    places = load_places()
    
    # Count by type
    type_counts = {}
    for place in places:
        for place_type in place.get('types', []):
            type_counts[place_type] = type_counts.get(place_type, 0) + 1
    
    return jsonify({
        'total_places': len(places),
        'type_counts': type_counts
    })


if __name__ == '__main__':
    print("="*70)
    print("Nouakchott Places Manager")
    print("="*70)
    print(f"\nLoading places from: {PLACES_FILE}")
    places = load_places()
    print(f"Total places loaded: {len(places)}")
    print("\nStarting web server...")
    print("\nPress Ctrl+C to stop the server")
    print("="*70)
    
    # Get port from environment variable (for deployment) or use 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
