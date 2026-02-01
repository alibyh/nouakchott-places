#!/usr/bin/env python3
"""
===================================================================================
Google Places Extractor for Nouakchott, Mauritania
===================================================================================

WHY THIS APPROACH IS NECESSARY:

The Google Places API does not provide a "list all places in a city" endpoint.
Constraints that require our systematic approach:

1. RESULT TRUNCATION: Nearby Search returns max 60 results (3 pages × 20) per query,
   even if thousands of places exist in the area. Google prioritizes by "prominence"
   and ranking algorithms we cannot control.

2. NO COMPREHENSIVE QUERY: A single large search over an entire city will only return
   the most "prominent" places, missing the vast majority of businesses and locations.

3. SOLUTION - GRID + TYPE ITERATION:
   - Divide the city into small grid cells (lat/lng squares)
   - For each cell, query multiple times with different place types
   - This multiplies our coverage: N cells × M types × 60 results
   - Small cells ensure we don't hit the 60-result cap per query
   - Type filtering changes ranking/results, exposing different places

KNOWN LIMITATIONS (inherent to the API):

1. Hidden/Unlisted Places: Some places may not be in Google's database
2. Ranking Bias: Google's algorithms determine what's "prominent" - we can't override
3. API Rate Limits: 100,000 requests/month on free tier (check your quota)
4. Radius Cap: Max 50km radius, but smaller is better for completeness
5. Coverage Gaps: Despite best efforts, some places may remain invisible to the API

EXPECTED BEHAVIOR:

This script is designed to run for hours and may make thousands of API requests.
It will systematically scan every grid cell with every place type, handle pagination,
deduplicate results, save checkpoints, and produce a single comprehensive output file.

===================================================================================
"""

import googlemaps
import json
import time
import logging
import sys
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
import os
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class Config:
    """Centralized configuration for the extraction process."""
    
    # API Configuration
    API_KEY: str = os.getenv("GOOGLE_PLACES_API_KEY", "YOUR_API_KEY_HERE")
    
    # Nouakchott Bounding Box (approximate coverage)
    # These coordinates ensure complete coverage of Nouakchott metropolitan area
    BBOX_NORTH: float = 18.15  # Northern boundary
    BBOX_SOUTH: float = 17.95  # Southern boundary
    BBOX_EAST: float = -15.85  # Eastern boundary
    BBOX_WEST: float = -16.10  # Western boundary
    
    # Grid Configuration
    # Smaller cells = more complete coverage but more API calls
    # These values create ~100-200 cells, adjust based on your quota
    GRID_LAT_DIVISIONS: int = 10  # Number of divisions along latitude
    GRID_LNG_DIVISIONS: int = 10  # Number of divisions along longitude
    
    # Search Parameters
    SEARCH_RADIUS_METERS: int = 1000  # Radius for each grid cell center
    
    # Place Types to Query
    # Comprehensive list covering most business/location categories
    # Each type will be queried for every grid cell
    PLACE_TYPES: List[str] = field(default_factory=lambda: [
        # Essential/Common
        "restaurant", "cafe", "bar", "food",
        "lodging", "hotel", "mosque",
        "school", "university", "library",
        "hospital", "pharmacy", "doctor", "dentist",
        "bank", "atm",
        "store", "supermarket", "shopping_mall",
        "gas_station", "car_repair",
        "bus_station", "taxi_stand", "airport",
        
        # Services
        "laundry", "beauty_salon", "hair_care", "spa",
        "gym", "stadium", "park",
        "movie_theater", "night_club", "casino",
        "travel_agency", "real_estate_agency",
        "lawyer", "accountant", "insurance_agency",
        "post_office", "courthouse", "embassy",
        "police", "fire_station", "local_government_office",
        
        # Retail
        "bakery", "electronics_store", "furniture_store",
        "hardware_store", "home_goods_store",
        "clothing_store", "shoe_store", "jewelry_store",
        "book_store", "florist", "pet_store",
        
        # Automotive
        "car_dealer", "car_rental", "car_wash", "parking",
        
        # Religious & Cultural
        "church", "hindu_temple", "synagogue",
        "museum", "art_gallery", "aquarium", "zoo",
        
        # Professional
        "veterinary_care", "plumber", "electrician",
        "locksmith", "roofing_contractor", "painter",
        "moving_company", "storage",
        
        # Financial
        "finance", "accounting",
        
        # Miscellaneous
        "point_of_interest", "establishment",
        "cemetery", "funeral_home",
        "campground", "rv_park",
        "tourist_attraction", "amusement_park",
    ])
    
    # Also perform generic searches without type filtering
    INCLUDE_GENERIC_SEARCH: bool = True
    
    # Rate Limiting & Retry
    DELAY_BETWEEN_REQUESTS_SECONDS: float = 0.5  # Avoid hitting rate limits
    PAGINATION_DELAY_SECONDS: float = 2.5  # Google requires ~2s before next_page_token
    MAX_RETRIES: int = 5
    INITIAL_RETRY_DELAY_SECONDS: float = 1.0  # For exponential backoff
    
    # Output Configuration
    OUTPUT_FILE: str = "nouakchott_places.json"
    CHECKPOINT_FILE: str = "extraction_checkpoint.json"
    LOG_FILE: str = "extraction.log"
    
    # Resume Capability
    ENABLE_CHECKPOINTING: bool = True
    CHECKPOINT_INTERVAL: int = 10  # Save checkpoint every N grid cells


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(config: Config) -> logging.Logger:
    """Configure logging to both file and console."""
    logger = logging.getLogger("PlacesExtractor")
    logger.setLevel(logging.INFO)
    
    # File handler
    fh = logging.FileHandler(config.LOG_FILE, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    
    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Place:
    """Represents a place with the required output schema."""
    place_id: str
    name: str
    types: List[str]
    latitude: float
    longitude: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary matching exact output schema."""
        return {
            "place_id": self.place_id,
            "name": self.name,
            "types": self.types,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }


@dataclass
class GridCell:
    """Represents a single grid cell to search."""
    row: int
    col: int
    center_lat: float
    center_lng: float


@dataclass
class Checkpoint:
    """State for resume capability."""
    last_completed_cell_index: int
    total_unique_places: int
    total_api_calls: int
    total_duplicates_skipped: int
    timestamp: str


# ============================================================================
# GRID GENERATION
# ============================================================================

def generate_grid(config: Config) -> List[GridCell]:
    """
    Generate grid cells covering the entire city bounding box.
    Returns a list of GridCell objects with center coordinates.
    """
    cells = []
    
    lat_step = (config.BBOX_NORTH - config.BBOX_SOUTH) / config.GRID_LAT_DIVISIONS
    lng_step = (config.BBOX_EAST - config.BBOX_WEST) / config.GRID_LNG_DIVISIONS
    
    for row in range(config.GRID_LAT_DIVISIONS):
        for col in range(config.GRID_LNG_DIVISIONS):
            # Calculate center of this cell
            center_lat = config.BBOX_SOUTH + (row + 0.5) * lat_step
            center_lng = config.BBOX_WEST + (col + 0.5) * lng_step
            
            cells.append(GridCell(
                row=row,
                col=col,
                center_lat=center_lat,
                center_lng=center_lng
            ))
    
    return cells


# ============================================================================
# API INTERACTION
# ============================================================================

class PlacesExtractor:
    """Main extraction engine with retry logic and deduplication."""
    
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.gmaps = googlemaps.Client(key=config.API_KEY)
        
        # Deduplication tracking
        self.seen_place_ids: Set[str] = set()
        self.places: Dict[str, Place] = {}  # place_id -> Place
        
        # Statistics
        self.total_api_calls = 0
        self.total_duplicates_skipped = 0
        self.current_cell_index = 0
        
    def search_with_retry(
        self, 
        location: Tuple[float, float], 
        radius: int,
        place_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Execute a nearby search with exponential backoff on failure.
        Handles pagination automatically.
        """
        all_results = []
        next_page_token = None
        page_num = 0
        
        while True:
            retry_count = 0
            delay = self.config.INITIAL_RETRY_DELAY_SECONDS
            
            while retry_count < self.config.MAX_RETRIES:
                try:
                    self.total_api_calls += 1
                    
                    # Build request parameters
                    kwargs = {
                        'location': location,
                        'radius': radius,
                    }
                    
                    if place_type:
                        kwargs['type'] = place_type
                    
                    if next_page_token:
                        kwargs['page_token'] = next_page_token
                    
                    # Execute search
                    response = self.gmaps.places_nearby(**kwargs)
                    
                    if response.get('status') not in ['OK', 'ZERO_RESULTS']:
                        self.logger.warning(
                            f"API returned status: {response.get('status')} "
                            f"for location {location}, type: {place_type}"
                        )
                    
                    # Extract results
                    results = response.get('results', [])
                    all_results.extend(results)
                    page_num += 1
                    
                    # Check for next page
                    next_page_token = response.get('next_page_token')
                    
                    if next_page_token:
                        # Google requires a short delay before using next_page_token
                        self.logger.debug(
                            f"Page {page_num} fetched, waiting {self.config.PAGINATION_DELAY_SECONDS}s "
                            f"for next page token..."
                        )
                        time.sleep(self.config.PAGINATION_DELAY_SECONDS)
                    else:
                        # No more pages
                        break
                    
                    # Small delay between pages
                    time.sleep(self.config.DELAY_BETWEEN_REQUESTS_SECONDS)
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    retry_count += 1
                    self.logger.warning(
                        f"API error (attempt {retry_count}/{self.config.MAX_RETRIES}): {e}"
                    )
                    
                    if retry_count >= self.config.MAX_RETRIES:
                        self.logger.error(
                            f"Max retries exceeded for location {location}, type: {place_type}"
                        )
                        return all_results  # Return what we have so far
                    
                    # Exponential backoff
                    time.sleep(delay)
                    delay *= 2
            
            if not next_page_token:
                break
        
        return all_results
    
    def process_result(self, result: Dict) -> None:
        """
        Process a single place result, extract required fields,
        and add to collection if not a duplicate.
        """
        place_id = result.get('place_id')
        
        if not place_id:
            self.logger.warning(f"Place without place_id: {result.get('name', 'unknown')}")
            return
        
        # Deduplication check
        if place_id in self.seen_place_ids:
            self.total_duplicates_skipped += 1
            return
        
        # Extract required fields
        name = result.get('name', '')
        types = result.get('types', [])
        
        geometry = result.get('geometry', {})
        location = geometry.get('location', {})
        latitude = location.get('lat', 0.0)
        longitude = location.get('lng', 0.0)
        
        # Create Place object
        place = Place(
            place_id=place_id,
            name=name,
            types=types,
            latitude=latitude,
            longitude=longitude
        )
        
        # Add to collection
        self.seen_place_ids.add(place_id)
        self.places[place_id] = place
    
    def search_grid_cell(self, cell: GridCell) -> None:
        """
        Search a single grid cell with all configured place types
        plus a generic search.
        """
        location = (cell.center_lat, cell.center_lng)
        radius = self.config.SEARCH_RADIUS_METERS
        
        search_types = self.config.PLACE_TYPES.copy()
        
        # Add generic search
        if self.config.INCLUDE_GENERIC_SEARCH:
            search_types.append(None)  # None = no type filter
        
        for idx, place_type in enumerate(search_types):
            type_label = place_type if place_type else "generic"
            
            self.logger.info(
                f"  Type {idx+1}/{len(search_types)}: {type_label} "
                f"(unique places so far: {len(self.places)})"
            )
            
            # Execute search with pagination
            results = self.search_with_retry(
                location=location,
                radius=radius,
                place_type=place_type
            )
            
            # Process all results
            for result in results:
                self.process_result(result)
            
            # Rate limiting delay
            time.sleep(self.config.DELAY_BETWEEN_REQUESTS_SECONDS)
    
    def extract_all_places(self, grid: List[GridCell], start_from: int = 0) -> None:
        """
        Main extraction loop: iterate over all grid cells and extract places.
        Supports resuming from a specific cell index.
        """
        total_cells = len(grid)
        
        self.logger.info(f"Starting extraction from cell {start_from}/{total_cells}")
        self.logger.info(f"Grid: {self.config.GRID_LAT_DIVISIONS}×{self.config.GRID_LNG_DIVISIONS} cells")
        self.logger.info(f"Place types to query: {len(self.config.PLACE_TYPES)}")
        self.logger.info(f"Search radius: {self.config.SEARCH_RADIUS_METERS}m")
        
        for idx in range(start_from, total_cells):
            cell = grid[idx]
            self.current_cell_index = idx
            
            self.logger.info(
                f"\n{'='*70}\n"
                f"Cell {idx+1}/{total_cells} - "
                f"Row {cell.row}, Col {cell.col} - "
                f"Center: ({cell.center_lat:.5f}, {cell.center_lng:.5f})\n"
                f"{'='*70}"
            )
            
            # Search this cell
            self.search_grid_cell(cell)
            
            # Checkpoint if enabled
            if self.config.ENABLE_CHECKPOINTING and (idx + 1) % self.config.CHECKPOINT_INTERVAL == 0:
                self.save_checkpoint()
            
            self.logger.info(
                f"Cell {idx+1} complete. "
                f"Total unique: {len(self.places)}, "
                f"Duplicates skipped: {self.total_duplicates_skipped}, "
                f"API calls: {self.total_api_calls}"
            )
        
        self.logger.info(f"\n{'='*70}\nExtraction complete!\n{'='*70}")
        self.logger.info(f"Total unique places: {len(self.places)}")
        self.logger.info(f"Total duplicates skipped: {self.total_duplicates_skipped}")
        self.logger.info(f"Total API calls: {self.total_api_calls}")
    
    def save_checkpoint(self) -> None:
        """Save current progress for resume capability."""
        checkpoint = Checkpoint(
            last_completed_cell_index=self.current_cell_index,
            total_unique_places=len(self.places),
            total_api_calls=self.total_api_calls,
            total_duplicates_skipped=self.total_duplicates_skipped,
            timestamp=datetime.now().isoformat()
        )
        
        checkpoint_data = {
            'checkpoint': asdict(checkpoint),
            'seen_place_ids': list(self.seen_place_ids),
            'places': [place.to_dict() for place in self.places.values()]
        }
        
        with open(self.config.CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Checkpoint saved: {self.config.CHECKPOINT_FILE}")
    
    def load_checkpoint(self) -> Optional[int]:
        """
        Load checkpoint if it exists.
        Returns the cell index to resume from, or None if no checkpoint.
        """
        if not os.path.exists(self.config.CHECKPOINT_FILE):
            return None
        
        try:
            with open(self.config.CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            checkpoint = checkpoint_data['checkpoint']
            
            # Restore state
            self.seen_place_ids = set(checkpoint_data['seen_place_ids'])
            
            for place_dict in checkpoint_data['places']:
                place = Place(**place_dict)
                self.places[place.place_id] = place
            
            self.total_api_calls = checkpoint['total_api_calls']
            self.total_duplicates_skipped = checkpoint['total_duplicates_skipped']
            
            resume_from = checkpoint['last_completed_cell_index'] + 1
            
            self.logger.info(f"Checkpoint loaded from {checkpoint['timestamp']}")
            self.logger.info(f"Resuming from cell {resume_from}")
            self.logger.info(f"Restored {len(self.places)} places")
            
            return resume_from
            
        except Exception as e:
            self.logger.error(f"Failed to load checkpoint: {e}")
            return None
    
    def save_final_output(self) -> None:
        """
        Save all places to final JSON output file.
        Sorted alphabetically by name, pretty-printed, UTF-8.
        """
        # Convert to list and sort by name
        places_list = [place.to_dict() for place in self.places.values()]
        places_list.sort(key=lambda x: x['name'].lower())
        
        # Write to file
        with open(self.config.OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(places_list, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Final output saved: {self.config.OUTPUT_FILE}")
        self.logger.info(f"Total places in output: {len(places_list)}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point."""
    # Load configuration
    config = Config()
    
    # Validate API key
    if config.API_KEY == "YOUR_API_KEY_HERE" or not config.API_KEY:
        print("ERROR: Please set GOOGLE_PLACES_API_KEY environment variable")
        print("or update the API_KEY in the Config class.")
        print("\nExample:")
        print("  export GOOGLE_PLACES_API_KEY='your-api-key-here'")
        print("  python extract_places.py")
        sys.exit(1)
    
    # Setup logging
    logger = setup_logging(config)
    
    logger.info("="*70)
    logger.info("Google Places Extractor - Nouakchott, Mauritania")
    logger.info("="*70)
    logger.info(f"Started at: {datetime.now().isoformat()}")
    
    # Generate grid
    logger.info("Generating search grid...")
    grid = generate_grid(config)
    logger.info(f"Generated {len(grid)} grid cells")
    
    # Create extractor
    extractor = PlacesExtractor(config, logger)
    
    # Check for checkpoint
    resume_from = 0
    if config.ENABLE_CHECKPOINTING:
        loaded_resume = extractor.load_checkpoint()
        if loaded_resume is not None:
            resume_from = loaded_resume
    
    # Execute extraction
    try:
        extractor.extract_all_places(grid, start_from=resume_from)
        
        # Save final output
        extractor.save_final_output()
        
        # Clean up checkpoint file
        if config.ENABLE_CHECKPOINTING and os.path.exists(config.CHECKPOINT_FILE):
            os.remove(config.CHECKPOINT_FILE)
            logger.info("Checkpoint file removed (extraction complete)")
        
        logger.info(f"\nCompleted at: {datetime.now().isoformat()}")
        logger.info("SUCCESS: Extraction finished successfully!")
        
    except KeyboardInterrupt:
        logger.warning("\n\nExtraction interrupted by user")
        logger.info("Saving checkpoint for resume...")
        extractor.save_checkpoint()
        logger.info("You can resume by running the script again")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"\n\nFATAL ERROR: {e}", exc_info=True)
        logger.info("Saving checkpoint for resume...")
        extractor.save_checkpoint()
        sys.exit(1)


if __name__ == "__main__":
    main()
