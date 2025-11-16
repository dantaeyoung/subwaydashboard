# Greenpoint Transit Tracker

Real-time NYC G Train and East River Ferry schedules for Greenpoint, displayed in your macOS menu bar using SwiftBar.

## Current Status

✅ **Working**: G Train real-time arrivals (both Queens-bound and Church Ave-bound)
✅ **Working**: NYC Ferry arrivals at Greenpoint (stop ID: 18)
⚠️ **Limitation**: Ferry direction detection not implemented yet (all ferries show under "Hunters Point")

## What It Shows

- **G Train (Greenpoint Ave)**: Next 3 arrivals for Queens-bound and Church Ave-bound trains
- **East River Ferry (Greenpoint)**: Next ferry arrivals (currently all shown under "Hunters Point")
- **Menu Bar**: Shows soonest arrival across all routes (e.g., "G→Queens: 3min", "Ferry→HP: Now")
- **Dropdown**: Click to see all upcoming trains and ferries

## Setup Instructions

### 1. Install SwiftBar

Download and install SwiftBar from: https://swiftbar.app

Or install via Homebrew:
```bash
brew install swiftbar
```

### 2. Install Python Dependencies

**Using UV (recommended)**:
```bash
uv pip install --system -r requirements.txt
```

**Or using pip**:
```bash
pip3 install -r requirements.txt
```

### 3. Configure SwiftBar

1. Open SwiftBar from your menu bar
2. Click "Preferences"
3. Set the "Plugin Folder" to this directory: `/Users/provolot/github/ferryschedule`
4. SwiftBar will automatically detect `greenpoint-transit.30s.py` and start running it

### 4. Verify It's Working

You should see a 🚇 icon in your menu bar with the next arrival time. Click it to see all routes.

## Customization

### Change Refresh Rate

Rename the file to adjust how often it updates:
- `greenpoint-transit.10s.py` - Every 10 seconds (more battery usage)
- `greenpoint-transit.30s.py` - Every 30 seconds (default, recommended)
- `greenpoint-transit.1m.py` - Every 1 minute (less battery usage)

### Customize Display

Edit `greenpoint-transit.30s.py` to:
- Change the menu bar format (line ~150)
- Modify which routes are shown
- Adjust the number of upcoming arrivals (change `[:3]` to show more/fewer)

## Known Limitations

**Ferry Direction Detection**: Ferry arrivals are shown, but direction (Hunters Point vs. Wall Street) cannot be reliably determined from the realtime feed. Currently, all ferries are displayed under "Hunters Point". To fix this, we would need to:
1. Map trip IDs to their route patterns (analyze which stops each trip visits)
2. Determine terminal destinations based on stop sequences
3. Update the logic to categorize ferries by direction

**Ferry Service Hours**: The NYC Ferry GTFS realtime feed only shows ferries that are actively running. During off-peak hours or when no ferries are scheduled, you'll see "No data". This is expected behavior.

If you'd like to help improve ferry direction detection, check out the `show_current_feed.py` and `analyze_ferry.py` scripts!

## Troubleshooting

### "No data" shown for G trains
- Check your internet connection
- MTA API might be temporarily down
- Try running the script manually to see error messages:
  ```bash
  python3 greenpoint-transit.30s.py
  ```
- If you see actual train times when running manually, but SwiftBar shows "No data", try restarting SwiftBar

### Script not appearing in SwiftBar
- Make sure the file is executable: `chmod +x greenpoint-transit.30s.py`
- Check that the plugin folder is set correctly in SwiftBar preferences (should be `/Users/provolot/github/ferryschedule`)
- Click "Refresh All" in SwiftBar menu
- Restart SwiftBar

### Missing dependencies
Run: `uv pip install --system -r requirements.txt`

Or: `pip3 install -r requirements.txt`

## How It Works

1. Uses the `nyct-gtfs` Python library to fetch real-time G train data from MTA's GTFS feed
2. Uses a separate subprocess script (`get_ferry.py`) to fetch ferry data to avoid protobuf conflicts
3. Filters for Greenpoint Avenue station (G train stops: G26N, G26S; Ferry stop: 18)
4. Calculates minutes until each train/ferry arrival
5. Formats output according to SwiftBar's specification:
   - Menu bar shows soonest arrival across all routes
   - Dropdown shows next 3 arrivals for each route
6. Refreshes every 30 seconds (configurable by renaming the file)

## Technical Details

- **MTA G Train**: Uses `nyct-gtfs` library which wraps the official MTA GTFS-realtime feed
  - Feed URL: `https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g`
  - No API key required (as of 2025)
  - Returns protobuf-encoded realtime data
- **NYC Ferry**: Uses `gtfs-realtime-bindings` to parse ferry data
  - Feed URL: `http://nycferry.connexionz.net/rtt/public/utility/gtfsrealtime.aspx/tripupdate`
  - Greenpoint stop ID: 18
  - Runs in separate subprocess to avoid protobuf conflicts with nyct-gtfs

## Required Files

For the SwiftBar plugin to work, you need:
1. **`greenpoint-transit.30s.py`** - Main plugin script
2. **`get_ferry.py`** - Subprocess helper for ferry data
3. **Python dependencies** installed (via `requirements.txt`)

Both scripts must be in the same directory (your SwiftBar plugin folder).

## Contributing

Contributions welcome! Particularly:
- Help determining ferry direction from trip patterns
- UI/UX improvements
- Additional transit routes

## License

Free to use and modify
