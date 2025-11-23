# MTA G Train Display Generator

Creates an 800x600 PNG image showing real-time G train arrivals at Greenpoint Ave station with current weather. Meant to be used with [kindle-dash](https://github.com/pascalw/kindle-dash) and a jailbroken Kindle.

![MTA Display Example](schedule_example.png)

## Features

- **4 G Train arrivals** - 2 Court Square-bound, 2 Church Ave-bound
- **Current weather** - Temperature and conditions from National Weather Service
- **Current time** - Displayed in footer
- **Clean MTA-style design** - Gray background, green G train circles, bold Helvetica font
- **Antialiased rendering** - Smooth text and graphics
- **Rotation option** - Landscape (800x600) or portrait (600x800) mode
         
## Installation

From the project root directory, using uv (recommended):

```bash
uv pip install -r requirements.txt
```

Or using pip:
```bash
pip3 install -r requirements.txt
```

Required dependencies:
- `Pillow` - Image generation
- `nyct-gtfs` - Real-time G train data
- `requests` - Weather API calls

### Font Requirements

**For best results (recommended):** Place a copy of `Helvetica.ttc` in the `mta-display/` folder. The script will automatically use it for true MTA-style rendering.

**Font rendering by platform:**
- **macOS with Helvetica.ttc**: Full support including bold variants
- **Linux with Helvetica.ttc**: Helvetica is used but may not render bold properly (Pillow limitation with .ttc files on Linux)
- **Linux without Helvetica.ttc**: Uses system fonts (DejaVu Sans, Liberation Sans, or FreeSans)

**On Linux** (if not using Helvetica.ttc), install system fonts:
```bash
sudo apt-get install fonts-dejavu fonts-liberation
```

**Note:** Helvetica is a proprietary font. You can obtain it from:
- macOS: `/System/Library/Fonts/Helvetica.ttc`
- Commercial license from Monotype
- Adobe Fonts subscription

## Usage

### Basic Usage

Generate a landscape display (800x600):

```bash
python3 mta_display.py
```

### Portrait Mode

Rotate 90° counter-clockwise for portrait display (600x800):

```bash
python3 mta_display.py --rotate
# or
python3 mta_display.py -r
```

## Output

The script generates `schedule.png` in the current directory.

## Customization

Edit `mta_display.py` to customize:

- **Colors** - Change `BG_COLOR`, `LINE_COLOR`, `SEPARATOR_COLOR`
- **Dimensions** - Modify `WIDTH` and `HEIGHT`
- **Number of trains** - Adjust `limit` parameter in `get_all_trains()`
- **Location** - Update coordinates in `get_weather()` for different location

## How It Works

1. Fetches real-time G train data from MTA's GTFS feed using `nyct-gtfs`
2. Gets current weather from National Weather Service API (no API key required)
3. Renders at 2x resolution for antialiasing
4. Draws:
   - Green G train circles with bold text
   - Station names (Court Square / Church Ave) in bold
   - Arrival times with "MIN" label
   - Dark separators between entries
   - Footer with time and weather
5. Scales down to target size with high-quality filtering
6. Optionally rotates 90° CCW for portrait displays

## Technical Details

- **Font**: Helvetica (bold for stations, regular for times)
- **Antialiasing**: 2x supersampling with LANCZOS downscaling
- **Weather**: National Weather Service API (free, no key needed)
- **MTA Data**: GTFS realtime feed for G train
- **Station**: Greenpoint Ave (G26N northbound, G26S southbound)

## Use Cases

- Digital photo frames
- Dashboard displays
- E-ink displays
- Information screens
- Personal monitors
