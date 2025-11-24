# Warning: VIBECODED

# MTA Train Display Generator

Creates an 800x600 PNG image showing real-time subway train arrivals with current weather. Meant to be used with [kindle-dash](https://github.com/pascalw/kindle-dash) and a jailbroken Kindle.

(Station is hardcoded)

![MTA Display Example](schedule_example.png)

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
- `python-dateutil` - Date parsing for sunrise/sunset
- `pytz` - Timezone handling
- `cairosvg` - SVG icon rendering

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
uv run mta_display.py
```

### Portrait Mode

Rotate 90° counter-clockwise for portrait display (600x800):

```bash
uv run mta_display.py --rotate
# or
uv run mta_display.py -r
```

## Output

The script generates `schedule.png` in the current directory.

## Customization

Edit `mta_display.py` to customize:

- **Colors** - Change `BG_COLOR`, `LINE_COLOR`, `SEPARATOR_COLOR`
- **Dimensions** - Modify `WIDTH` and `HEIGHT`
- **Number of trains** - Adjust `limit` parameter in `get_all_trains()`
- **Location** - Update coordinates in `get_weather()` for different location

