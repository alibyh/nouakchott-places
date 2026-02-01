#!/usr/bin/env python3
"""
Data analysis script for extracted places.
Provides insights into the collected data.
"""

import json
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Any
import os


def load_places(filename: str = "nouakchott_places.json") -> List[Dict]:
    """Load places from JSON file."""
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        print("Run extract_places.py first to generate data.")
        sys.exit(1)
    
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_places(places: List[Dict]) -> None:
    """Perform comprehensive analysis of extracted places."""
    
    print("="*70)
    print("GOOGLE PLACES DATA ANALYSIS - Nouakchott, Mauritania")
    print("="*70)
    print()
    
    # Basic Statistics
    print("📊 BASIC STATISTICS")
    print("-"*70)
    total = len(places)
    print(f"Total unique places: {total:,}")
    print()
    
    # Type Distribution
    print("🏷️  PLACE TYPE DISTRIBUTION (Top 20)")
    print("-"*70)
    
    all_types = []
    for place in places:
        all_types.extend(place.get('types', []))
    
    type_counts = Counter(all_types)
    
    for idx, (place_type, count) in enumerate(type_counts.most_common(20), 1):
        percentage = (count / total) * 100
        bar_length = int(percentage / 2)  # Scale for display
        bar = "█" * bar_length
        print(f"{idx:2}. {place_type:30} {count:5,} ({percentage:5.1f}%) {bar}")
    
    print()
    
    # Primary Type Distribution
    print("🎯 PRIMARY TYPE DISTRIBUTION (Top 15)")
    print("-"*70)
    print("(First type listed for each place)")
    print()
    
    primary_types = [place['types'][0] if place.get('types') else 'unknown' 
                     for place in places]
    primary_counts = Counter(primary_types)
    
    for idx, (place_type, count) in enumerate(primary_counts.most_common(15), 1):
        percentage = (count / total) * 100
        print(f"{idx:2}. {place_type:30} {count:5,} ({percentage:5.1f}%)")
    
    print()
    
    # Geographic Distribution
    print("🗺️  GEOGRAPHIC DISTRIBUTION")
    print("-"*70)
    
    # Group by latitude (0.01 degree bins ≈ 1km)
    lat_bins = defaultdict(int)
    lng_bins = defaultdict(int)
    
    for place in places:
        lat = place.get('latitude', 0)
        lng = place.get('longitude', 0)
        lat_bin = round(lat, 2)
        lng_bin = round(lng, 2)
        lat_bins[lat_bin] += 1
        lng_bins[lng_bin] += 1
    
    print(f"Latitude range: {min(p['latitude'] for p in places):.4f} to {max(p['latitude'] for p in places):.4f}")
    print(f"Longitude range: {min(p['longitude'] for p in places):.4f} to {max(p['longitude'] for p in places):.4f}")
    print(f"Unique latitude bins (0.01° = ~1km): {len(lat_bins)}")
    print(f"Unique longitude bins (0.01° = ~1km): {len(lng_bins)}")
    
    # Find densest areas
    top_lat_bins = sorted(lat_bins.items(), key=lambda x: x[1], reverse=True)[:5]
    print()
    print("Densest latitude bands:")
    for lat, count in top_lat_bins:
        print(f"  Lat {lat:.2f}°: {count:,} places")
    
    print()
    
    # Name Analysis
    print("📝 NAME ANALYSIS")
    print("-"*70)
    
    names = [place.get('name', '') for place in places]
    name_lengths = [len(name) for name in names if name]
    
    if name_lengths:
        avg_length = sum(name_lengths) / len(name_lengths)
        print(f"Average name length: {avg_length:.1f} characters")
        print(f"Shortest name: {min(name_lengths)} chars - \"{min(names, key=len)}\"")
        print(f"Longest name: {max(name_lengths)} chars - \"{max(names, key=len)[:50]}...\"")
        
        # Common words in names
        words = []
        for name in names:
            words.extend(name.lower().split())
        
        word_counts = Counter(words)
        # Filter out very short words
        word_counts = {k: v for k, v in word_counts.items() if len(k) > 2}
        
        print()
        print("Most common words in place names:")
        for word, count in sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  \"{word}\": {count:,} times")
    
    print()
    
    # Coverage Assessment
    print("✅ COVERAGE ASSESSMENT")
    print("-"*70)
    
    # Places with multiple types (more detailed)
    multi_type_places = [p for p in places if len(p.get('types', [])) > 1]
    avg_types = sum(len(p.get('types', [])) for p in places) / total
    
    print(f"Places with multiple types: {len(multi_type_places):,} ({len(multi_type_places)/total*100:.1f}%)")
    print(f"Average types per place: {avg_types:.2f}")
    print()
    
    # Essential services coverage
    essential_types = {
        'hospital': 'Healthcare',
        'pharmacy': 'Pharmacy',
        'school': 'Education',
        'university': 'Higher Education',
        'bank': 'Banking',
        'atm': 'ATM',
        'restaurant': 'Dining',
        'supermarket': 'Grocery',
        'gas_station': 'Fuel',
        'mosque': 'Worship (Mosque)',
        'police': 'Emergency',
        'fire_station': 'Fire Safety',
    }
    
    print("Essential services found:")
    for key, label in essential_types.items():
        count = sum(1 for p in places if key in p.get('types', []))
        if count > 0:
            print(f"  {label:20} {count:4,} locations")
        else:
            print(f"  {label:20} ⚠️  None found")
    
    print()
    
    # Quality Checks
    print("🔍 DATA QUALITY")
    print("-"*70)
    
    # Check for potential issues
    places_no_name = sum(1 for p in places if not p.get('name'))
    places_no_types = sum(1 for p in places if not p.get('types'))
    places_zero_coords = sum(1 for p in places if p.get('latitude') == 0 or p.get('longitude') == 0)
    
    print(f"Places without name: {places_no_name} ({places_no_name/total*100:.2f}%)")
    print(f"Places without types: {places_no_types} ({places_no_types/total*100:.2f}%)")
    print(f"Places with zero coordinates: {places_zero_coords} ({places_zero_coords/total*100:.2f}%)")
    
    # Validate place_id uniqueness
    place_ids = [p.get('place_id') for p in places]
    unique_ids = len(set(place_ids))
    
    if unique_ids == total:
        print(f"✅ All place_ids are unique ({unique_ids:,})")
    else:
        duplicates = total - unique_ids
        print(f"⚠️  WARNING: {duplicates} duplicate place_ids found!")
    
    print()
    
    # Sample Places
    print("📋 SAMPLE PLACES (First 5)")
    print("-"*70)
    
    for idx, place in enumerate(places[:5], 1):
        print(f"{idx}. {place.get('name', 'Unknown')}")
        print(f"   ID: {place.get('place_id', 'N/A')}")
        print(f"   Types: {', '.join(place.get('types', [])[:3])}")
        print(f"   Location: ({place.get('latitude'):.5f}, {place.get('longitude'):.5f})")
        print()
    
    print("="*70)
    print("Analysis complete!")
    print("="*70)
    print()


def export_summary(places: List[Dict], output_file: str = "analysis_summary.txt") -> None:
    """Export analysis summary to text file."""
    
    total = len(places)
    all_types = []
    for place in places:
        all_types.extend(place.get('types', []))
    type_counts = Counter(all_types)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("GOOGLE PLACES EXTRACTION SUMMARY\n")
        f.write("="*70 + "\n\n")
        f.write(f"Total Places: {total:,}\n")
        f.write(f"Unique Place Types: {len(type_counts)}\n\n")
        
        f.write("Top 20 Place Types:\n")
        f.write("-"*70 + "\n")
        for idx, (place_type, count) in enumerate(type_counts.most_common(20), 1):
            percentage = (count / total) * 100
            f.write(f"{idx:2}. {place_type:30} {count:5,} ({percentage:5.1f}%)\n")
        
        f.write("\n")
        f.write("Geographic Coverage:\n")
        f.write("-"*70 + "\n")
        f.write(f"Latitude range: {min(p['latitude'] for p in places):.4f} to {max(p['latitude'] for p in places):.4f}\n")
        f.write(f"Longitude range: {min(p['longitude'] for p in places):.4f} to {max(p['longitude'] for p in places):.4f}\n")
    
    print(f"Summary exported to: {output_file}")


def main():
    """Main entry point."""
    
    # Allow custom filename as argument
    filename = sys.argv[1] if len(sys.argv) > 1 else "nouakchott_places.json"
    
    # Load data
    print(f"Loading data from {filename}...")
    places = load_places(filename)
    print(f"Loaded {len(places):,} places\n")
    
    # Analyze
    analyze_places(places)
    
    # Export summary
    export_summary(places)
    
    print("\nFor more analysis, you can use jq:")
    print("  jq '[.[].types[0]] | group_by(.) | map({type:.[0], count:length})' nouakchott_places.json")
    print()


if __name__ == "__main__":
    main()
