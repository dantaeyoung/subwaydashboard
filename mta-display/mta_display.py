#!/usr/bin/env python3
"""
MTA G Train Display Generator
Creates an 800x600 PNG showing next trains at Greenpoint G station
"""

from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from nyct_gtfs import NYCTFeed
import requests
import sys
import os
import platform

# Station IDs
G_TRAIN_GREENPOINT_NORTH = "G26N"  # Queens-bound
G_TRAIN_GREENPOINT_SOUTH = "G26S"  # Church Ave-bound

# Display settings
WIDTH = 800
HEIGHT = 600


BG_COLOR = (255, 255, 255)  #  background
TEXT_COLOR = (0, 0, 0)  # White text
LINE_COLOR = (131, 190, 82)  # G train green color
SEPARATOR_COLOR = (30, 30, 30)  # Dark blue separator
HEADER_BG = (30, 30, 30)  # Dark gray footer background
HEADER_TEXT = (255, 255, 255)  # White header text

"""
BG_COLOR = (37, 37, 37)  # Dark background
TEXT_COLOR = (255, 255, 255)  # White text
LINE_COLOR = (131, 190, 82)  # G train green color
SEPARATOR_COLOR = (10, 10, 10)  # Dark blue separator
HEADER_BG = (10, 10, 10)  # Dark gray footer background
HEADER_TEXT = (255, 255, 255)  # White header text
"""

def get_all_trains(limit=4):
    """Get next arrivals for both directions - Queens-bound first, then Church Ave-bound"""
    try:
        feed = NYCTFeed("G")
        trains_list = feed.trips

        queens_arrivals = []
        church_arrivals = []
        now = datetime.now()

        # Get Queens-bound trains
        for train in trains_list:
            for stop_update in train.stop_time_updates:
                if stop_update.stop_id == G_TRAIN_GREENPOINT_NORTH and stop_update.arrival:
                    minutes_away = int((stop_update.arrival - now).total_seconds() / 60)
                    if minutes_away >= 0:
                        queens_arrivals.append({
                            'minutes': minutes_away,
                            'destination': 'Court Square'
                        })
                    break

        # Get Church Ave-bound trains
        for train in trains_list:
            for stop_update in train.stop_time_updates:
                if stop_update.stop_id == G_TRAIN_GREENPOINT_SOUTH and stop_update.arrival:
                    minutes_away = int((stop_update.arrival - now).total_seconds() / 60)
                    if minutes_away >= 0:
                        church_arrivals.append({
                            'minutes': minutes_away,
                            'destination': 'Church Ave'
                        })
                    break

        # Sort each direction by time, take 2 from each (total of 4)
        trains_per_direction = limit // 2
        queens_sorted = sorted(queens_arrivals, key=lambda x: x['minutes'])[:trains_per_direction]
        church_sorted = sorted(church_arrivals, key=lambda x: x['minutes'])[:trains_per_direction]

        # Return Queens first, then Church Ave
        return queens_sorted + church_sorted
    except Exception as e:
        print(f"Error fetching MTA data: {e}")
        return []


def get_weather():
    """Get current weather for Greenpoint, Brooklyn from National Weather Service"""
    try:
        # Greenpoint coordinates
        url = "https://api.weather.gov/points/40.7313,-73.9542"
        response = requests.get(url, headers={"User-Agent": "MTA Display App"}, timeout=5)
        data = response.json()
        forecast_url = data['properties']['forecast']

        forecast = requests.get(forecast_url, headers={"User-Agent": "MTA Display App"}, timeout=5)
        current = forecast.json()['properties']['periods'][0]

        temp = current['temperature']
        condition = current['shortForecast']

        # Shorten common conditions
        condition = condition.replace("Mostly", "M.").replace("Partly", "P.")
        condition = condition.replace("Cloudy", "Cloudy").replace("Sunny", "Sunny")

        # Limit length to prevent cutoff
        if len(condition) > 15:
            condition = condition[:15]

        return f"{temp}°F {condition}"
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return ""


def get_font_paths():
    """Get cross-platform font paths - prioritizes local Helvetica.ttc"""
    # First, check for local Helvetica.ttc in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_helvetica = os.path.join(script_dir, "Helvetica.ttf")
    local_helvetica_bold = os.path.join(script_dir, "Helvetica-Bold.ttf")

    if os.path.exists(local_helvetica) and os.path.exists(local_helvetica_bold):
        # Use the local bundled Helvetica font
        return {
            'regular': local_helvetica,
            'bold': local_helvetica_bold,
        }

    # Fall back to system fonts
    system = platform.system()

    if system == "Darwin":  # macOS
        return {
            'regular': "/System/Library/Fonts/Helvetica.ttc",
            'bold': "/System/Library/Fonts/Helvetica.ttc"
        }
    elif system == "Linux":
        # Try common Linux font paths
        linux_fonts = [
            ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ("/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
             "/usr/share/fonts/liberation/LiberationSans-Bold.ttf"),
            ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
            ("/usr/share/fonts/truetype/freefont/FreeSans.ttf",
             "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"),
        ]
        for regular_font, bold_font in linux_fonts:
            if os.path.exists(regular_font):
                # Use bold if it exists, otherwise use regular for both
                if not os.path.exists(bold_font):
                    bold_font = regular_font
                return {'regular': regular_font, 'bold': bold_font}

    # Fallback - try to find any truetype font
    return {'regular': None, 'bold': None}


def draw_antialiased_circle(img, center_x, center_y, radius, fill_color, text, text_font, font_index=0, use_font_index=True):
    """Draw an antialiased circle with centered text"""
    # Create a high-resolution temporary image (4x scale for better antialiasing)
    scale = 4
    size = radius * 2 * scale
    circle_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    circle_draw = ImageDraw.Draw(circle_img)

    # Draw circle at high resolution
    circle_draw.ellipse([0, 0, size, size], fill=fill_color)

    # Draw text at high resolution - scale up the font
    try:
        if use_font_index:
            # Use font index for .ttc files on macOS
            scaled_font = ImageFont.truetype(text_font.path, text_font.size * scale, index=font_index)
        else:
            # Don't use index - for .ttf files or .ttc on Linux
            scaled_font = ImageFont.truetype(text_font.path, text_font.size * scale)
    except Exception as e:
        # Last resort fallback - just use the original font
        print(f"Warning: Could not scale font for circle ({e}), using original size")
        scaled_font = text_font

    # Use anchor='mm' to center text at the middle
    circle_draw.text((size // 2, size // 2 + 35), text, fill=(255, 255, 255),
                    font=scaled_font, anchor='mm')

    # Resize down with high-quality antialiasing
    circle_img = circle_img.resize((radius * 2, radius * 2), Image.Resampling.LANCZOS)

    # Paste onto main image
    img.paste(circle_img, (center_x - radius, center_y - radius), circle_img)


def create_display_image(output_path="schedule.png", rotate=False, grayscale=False):
    """Create the MTA display image

    Args:
        output_path: Path to save the PNG file
        rotate: If True, rotate the image 90 degrees counter-clockwise
        grayscale: If True, make the image grayscale
    """

    # Create image at 2x resolution for better text antialiasing
    SCALE = 2
    SCALED_WIDTH = WIDTH * SCALE
    SCALED_HEIGHT = HEIGHT * SCALE

    img = Image.new('RGB', (SCALED_WIDTH, SCALED_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Get cross-platform font paths
    font_paths = get_font_paths()

    # Debug: Print font information
    print(f"Platform: {platform.system()}")
    print(f"Font paths: {font_paths}")

    # Determine if we can use font index - .ttc files work with index on macOS, but not always on Linux
    is_ttc = font_paths['bold'] and font_paths['bold'].endswith('.ttc')
    is_macos = platform.system() == "Darwin"
    use_font_index = is_ttc and is_macos

    try:
        if use_font_index:
            # macOS with .ttc - use index parameter for bold
            print(f"Loading fonts with index parameter (macOS .ttc)")
            header_font = ImageFont.truetype(font_paths['bold'], 36 * SCALE, index=1)
            line_font = ImageFont.truetype(font_paths['bold'], 62 * SCALE, index=1)
            dest_font = ImageFont.truetype(font_paths['bold'], 50 * SCALE, index=1)
            time_font = ImageFont.truetype(font_paths['bold'], 60 * SCALE, index=1)
            small_font = ImageFont.truetype(font_paths['bold'], 22 * SCALE, index=1)
        else:
            # Linux or separate font files (.ttf) - no index parameter
            # Note: On Linux with .ttc, we load it without index (may not get true bold)
            print(f"Loading fonts without index parameter (Linux or .ttf files)")
            print(f"Bold font path: {font_paths['bold']}, size: {36 * SCALE}")
            header_font = ImageFont.truetype(font_paths['bold'], 36 * SCALE)
            line_font = ImageFont.truetype(font_paths['bold'], 62 * SCALE)
            dest_font = ImageFont.truetype(font_paths['bold'], 50 * SCALE)
            time_font = ImageFont.truetype(font_paths['bold'], 60 * SCALE)
            small_font = ImageFont.truetype(font_paths['bold'], 22 * SCALE)
        print(f"Fonts loaded successfully!")
        print(f"Line font size: {line_font.size}")
    except Exception as e:
        # Fallback to default font if fonts are not available
        print(f"ERROR: Could not load fonts ({e})")
        import traceback
        traceback.print_exc()
        print("Falling back to default font")
        header_font = ImageFont.load_default()
        line_font = ImageFont.load_default()
        dest_font = ImageFont.load_default()
        time_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Get all trains (2 per direction = 4 total)
    all_trains = get_all_trains(limit=4)

    # Calculate even spacing for trains
    footer_height = 40
    available_height = HEIGHT - footer_height
    num_trains = len(all_trains)
    line_height = (available_height // num_trains) * SCALE

    # Starting Y position for train listings
    y_pos = (line_height // 2) - (30 * SCALE)  # Center vertically in each section

    # Draw all trains in sorted order
    for idx, train in enumerate(all_trains):
        minutes = train['minutes']
        destination = train['destination']

        # Draw G train circle with anti-aliasing and centered text
        circle_x = 70 * SCALE
        circle_y = y_pos + 30 * SCALE
        circle_radius = 50 * SCALE
        draw_antialiased_circle(img, circle_x, circle_y, circle_radius,
                               LINE_COLOR, "G", line_font, font_index=1, use_font_index=use_font_index)

        # Draw destination
        draw.text((140 * SCALE, y_pos + 18), destination, fill=TEXT_COLOR, font=dest_font)

        # Draw arrival time - center-aligned at a fixed x position
        time_text = str(minutes) if minutes > 0 else "Now"
        # Fixed x position for center of time numbers (about 100px from right edge)
        time_center_x = SCALED_WIDTH - 62 * SCALE

        if minutes > 0:
            draw.text((time_center_x, y_pos + 24 * SCALE), time_text, fill=TEXT_COLOR, font=time_font, anchor='mm')
        else:
            draw.text((SCALED_WIDTH - 85 * SCALE, y_pos + 32 * SCALE), time_text, fill=TEXT_COLOR, font=time_font, anchor='mm')

        # Draw "min" label if not "Now" - center-aligned below the number
        if minutes > 0:
            draw.text((time_center_x, y_pos + 64 * SCALE), "MIN", fill=TEXT_COLOR, font=small_font, anchor='mm')

        y_pos += line_height

        # Draw dark separator line between trains (not after the last one)
        if idx < len(all_trains) - 1:
            # Separator goes exactly at the row boundary
            line_y = (idx + 1) * line_height
            draw.line([(0, line_y), (SCALED_WIDTH, line_y)],
                     fill=SEPARATOR_COLOR, width=8 * SCALE)

    # Draw thin footer at bottom with time in bottom left
    footer_height_scaled = 40 * SCALE
    draw.rectangle([0, SCALED_HEIGHT - footer_height_scaled, SCALED_WIDTH, SCALED_HEIGHT], fill=HEADER_BG)

    # Add current time in bottom left corner
    current_time = datetime.now().strftime("%I:%M %p")
    draw.text((20 * SCALE, SCALED_HEIGHT - footer_height_scaled + 10 * SCALE), current_time, fill=HEADER_TEXT, font=small_font)

    # Add weather in bottom right corner
    weather = get_weather()
    if weather:
        weather_bbox = draw.textbbox((0, 0), weather, font=small_font)
        weather_width = weather_bbox[2] - weather_bbox[0]
        draw.text((SCALED_WIDTH - weather_width - 20 * SCALE, SCALED_HEIGHT - footer_height_scaled + 10 * SCALE),
                 weather, fill=HEADER_TEXT, font=small_font)

    # Scale image down to target size for antialiasing
    img = img.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

    # Rotate 90 degrees counter-clockwise if requested
    if rotate:
        img = img.transpose(Image.Transpose.ROTATE_90)

    if grayscale:
        img = img.convert("L")  # 8-bit grayscale

    # Save image
    img.save(output_path)
    print(f"Image saved to {output_path}" + (" (rotated 90° CCW)" if rotate else ""))


if __name__ == "__main__":
    # Check for --rotate flag
    rotate = "--rotate" in sys.argv or "-r" in sys.argv
    grayscale = "--grayscale" in sys.argv or "-g" in sys.argv
    create_display_image(rotate=rotate, grayscale=grayscale)
