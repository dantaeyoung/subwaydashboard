# Greenpoint Transit Tracker - SwiftBar Plugin

Real-time NYC G Train and East River Ferry schedules displayed in your macOS menu bar.

## What It Shows

- **G Train (Greenpoint Ave)**: Next 3 arrivals for Queens-bound and Church Ave-bound trains
- **East River Ferry (Greenpoint)**: Next ferry arrivals
- **Menu Bar**: Shows soonest arrival (e.g., "🚇")
- **Dropdown**: Click to see all upcoming trains and ferries

## Setup Instructions

### 1. Install SwiftBar

Download and install SwiftBar from: https://swiftbar.app

Or install via Homebrew:
```bash
brew install swiftbar
```

### 2. Install Python Dependencies

From the project root directory:

```bash
pip3 install -r requirements.txt
```

### 3. Configure SwiftBar

1. Open SwiftBar from your menu bar
2. Click "Preferences"
3. Set the "Plugin Folder" to this directory: `/path/to/ferryschedule/swiftbar`
4. SwiftBar will automatically detect `greenpoint-transit.30s.py` and start running it

### 4. Verify It's Working

You should see a 🚇 icon in your menu bar. Click it to see all routes.

## Customization

### Change Refresh Rate

Rename the file to adjust how often it updates:
- `greenpoint-transit.10s.py` - Every 10 seconds
- `greenpoint-transit.30s.py` - Every 30 seconds (default)
- `greenpoint-transit.1m.py` - Every 1 minute

## Files

- **greenpoint-transit.30s.py** - Main SwiftBar plugin script
- **get_ferry.py** - Helper script for fetching ferry data (runs in subprocess to avoid protobuf conflicts)

## Troubleshooting

### "No data" shown
- Check your internet connection
- MTA API might be temporarily down
- Try running manually: `python3 greenpoint-transit.30s.py`

### Script not appearing in SwiftBar
- Make sure the file is executable: `chmod +x greenpoint-transit.30s.py`
- Check that the plugin folder is set correctly in SwiftBar preferences
- Click "Refresh All" in SwiftBar menu

## How It Works

1. Uses `nyct-gtfs` library to fetch real-time G train data from MTA's GTFS feed
2. Uses separate subprocess (`get_ferry.py`) to fetch ferry data
3. Filters for Greenpoint Avenue station (G26N, G26S for trains; stop 18 for ferry)
4. Calculates minutes until each arrival
5. Updates every 30 seconds
