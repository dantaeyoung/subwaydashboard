# Development Scripts

This folder contains debugging and development scripts used during the development of the Greenpoint Transit tools.

## Scripts

### MTA/G Train Debugging
- **debug_transit.py** - Debug G train real-time data
- **show_current_feed.py** - Display current GTFS feed data

### Ferry Debugging
- **debug_ferry.py** - Debug ferry GTFS data
- **debug_ferry_function.py** - Test ferry data fetching functions
- **debug_get_ferry.py** - Test the get_ferry.py subprocess
- **test_ferry_18.py** - Test Greenpoint ferry stop (ID: 18)

### Ferry Analysis
- **analyze_ferry.py** - Analyze ferry trip patterns
- **analyze_ferry_trips.py** - Analyze ferry trip data to determine directions
- **map_ferry_stops.py** - Map ferry stop IDs to locations

## Data Files

- **ferry-gtfs-static.zip** - Static GTFS data for NYC Ferry
- **ferry-static-gtfs.zip** - Alternative ferry GTFS data

## Usage

These scripts are primarily for development and debugging purposes. They may require:
- Direct modification to change stop IDs or parameters
- Manual inspection of output
- Understanding of GTFS data structures

Most users won't need these scripts - use the main tools in `swiftbar/` and `mta-display/` instead.
