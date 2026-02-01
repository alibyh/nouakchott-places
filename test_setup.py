#!/usr/bin/env python3
"""
Quick test script to validate Google Places API setup.
Run this before the full extraction to ensure everything works.
"""

import os
import sys
import googlemaps
from datetime import datetime

def test_api_key():
    """Test if API key is valid and working."""
    print("="*60)
    print("Google Places API - Setup Test")
    print("="*60)
    print()
    
    # Check if API key is set
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("❌ FAIL: API key not found")
        print()
        print("Please set GOOGLE_PLACES_API_KEY environment variable:")
        print("  export GOOGLE_PLACES_API_KEY='your-api-key-here'")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    print()
    
    # Test API connection with a simple query
    print("Testing API connection...")
    print("Searching for places near Nouakchott center...")
    print()
    
    try:
        # Initialize client
        gmaps = googlemaps.Client(key=api_key)
        
        # Test query: Search near Nouakchott center
        center_lat = 18.0735
        center_lng = -15.9582
        
        response = gmaps.places_nearby(
            location=(center_lat, center_lng),
            radius=1000,
            type="restaurant"
        )
        
        # Check response
        status = response.get('status')
        results = response.get('results', [])
        
        if status == 'OK':
            print(f"✅ API Test SUCCESSFUL")
            print(f"   Status: {status}")
            print(f"   Results found: {len(results)}")
            print()
            
            if results:
                print("Sample result:")
                first = results[0]
                print(f"   Name: {first.get('name')}")
                print(f"   Place ID: {first.get('place_id')}")
                print(f"   Types: {', '.join(first.get('types', [])[:3])}")
                loc = first.get('geometry', {}).get('location', {})
                print(f"   Location: ({loc.get('lat')}, {loc.get('lng')})")
            
            print()
            print("="*60)
            print("✅ Setup is correct! Ready to run extraction.")
            print("="*60)
            print()
            print("Next step:")
            print("  python3 extract_places.py")
            return True
            
        elif status == 'ZERO_RESULTS':
            print("⚠️  WARNING: API works but returned zero results")
            print("   This might be normal for sparse areas")
            print("   Status: ZERO_RESULTS")
            print()
            print("The API is working, but you may want to check:")
            print("  - Bounding box coordinates")
            print("  - Search radius")
            return True
            
        elif status == 'REQUEST_DENIED':
            print("❌ FAIL: Request denied")
            print()
            print("Common causes:")
            print("  1. Places API not enabled in Google Cloud Console")
            print("  2. API key restrictions (check allowed APIs)")
            print("  3. Billing not enabled")
            print()
            print("Fix:")
            print("  1. Go to: https://console.cloud.google.com/apis/library")
            print("  2. Enable 'Places API'")
            print("  3. Enable billing in your project")
            return False
            
        elif status == 'OVER_QUERY_LIMIT':
            print("❌ FAIL: Query limit exceeded")
            print()
            print("You've exceeded your API quota.")
            print("Check: https://console.cloud.google.com/apis/api/places-backend.googleapis.com/quotas")
            return False
            
        else:
            print(f"⚠️  Unexpected status: {status}")
            print(f"Response: {response}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Error during API test")
        print(f"   Error: {e}")
        print()
        print("Common causes:")
        print("  1. No internet connection")
        print("  2. Invalid API key format")
        print("  3. googlemaps library not installed")
        print()
        print("Try:")
        print("  pip install googlemaps")
        return False


def test_dependencies():
    """Test if required packages are installed."""
    print("Checking dependencies...")
    
    try:
        import googlemaps
        print(f"✅ googlemaps library installed (version {googlemaps.__version__})")
        return True
    except ImportError:
        print("❌ FAIL: googlemaps library not installed")
        print()
        print("Install with:")
        print("  pip install googlemaps")
        return False


def main():
    """Run all tests."""
    print()
    
    # Test dependencies
    if not test_dependencies():
        sys.exit(1)
    
    print()
    
    # Test API
    if not test_api_key():
        sys.exit(1)
    
    print()


if __name__ == "__main__":
    main()
