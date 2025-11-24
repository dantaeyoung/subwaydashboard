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


#"""
BG_COLOR = (255, 255, 255)  #  background
TEXT_COLOR = (0, 0, 0)  # White text
LINE_COLOR = (131, 190, 82)  # G train green color
SEPARATOR_COLOR = (230, 230, 230)  # Dark blue separator
HEADER_BG = (80, 80, 80)  # Dark gray footer background
HEADER_TEXT = (255, 255, 255)  # White header text
WEATHER_LINE = (145, 145, 145)  # Weather graph line color
TIME_BAR_BG = (25, 25, 25)  # Slightly lighter background for time bar at bottom

def get_weather_icon(condition_text, is_sunrise=False, is_sunset=False):
    """Map weather condition text to icon filename using fuzzy matching"""
    condition_lower = condition_text.lower()

    # Special handling for sunrise/sunset
    if is_sunrise:
        return 'sunrise'
    if is_sunset:
        return 'sunset'

    # Icon mapping with fuzzy matching
    if 'thunder' in condition_lower or 'storm' in condition_lower and 'tropical' not in condition_lower:
        return 'thunderstorm'
    elif 'snow' in condition_lower or 'flurr' in condition_lower or 'blizzard' in condition_lower:
        return 'snow'
    elif 'rain' in condition_lower and 'heavy' in condition_lower:
        return 'heavy-rain'
    elif 'rain' in condition_lower or 'shower' in condition_lower:
        return 'rain'
    elif 'drizzle' in condition_lower:
        return 'drizzle'
    elif 'fog' in condition_lower or 'mist' in condition_lower:
        return 'fog'
    elif 'clear' in condition_lower and 'night' in condition_lower:
        return 'clear-night'
    elif 'partly' in condition_lower or 'p.' in condition_lower:
        return 'partly-cloudy'
    elif 'mostly' in condition_lower or 'm.' in condition_lower or 'overcast' in condition_lower or 'cloudy' in condition_lower:
        return 'cloudy'
    elif 'sunny' in condition_lower or 'clear' in condition_lower:
        return 'sunny'
    else:
        # Default to partly cloudy
        return 'partly-cloudy'


def load_png_icon(png_path, size):
    """Load a PNG icon and resize it to the specified size

    Args:
        png_path: Path to the PNG file
        size: Target size in pixels
    """
    try:
        # Load PNG and resize
        icon = Image.open(png_path)
        icon = icon.resize((size, size), Image.Resampling.LANCZOS)
        return icon
    except Exception as e:
        print(f"Error loading PNG {png_path}: {e}")
        # Return a blank image as fallback
        return Image.new('RGBA', (size, size), (0, 0, 0, 0))


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
    """Get current weather for Greenpoint, Brooklyn from National Weather Service

    Returns:
        tuple: (weather_text, main_icon, sun_icon, sun_text, hourly_forecast, sunrise_local, sunset_local) where:
            - weather_text: formatted temperature and condition string
            - main_icon: icon name for the main weather condition
            - sun_icon: icon name for sunrise/sunset
            - sun_text: formatted sunrise/sunset time text
            - hourly_forecast: list of 8 hourly forecast dicts with 'time', 'temp', 'condition', and 'hour_time' keys
            - sunrise_local: datetime object for today's sunrise in local timezone
            - sunset_local: datetime object for today's sunset in local timezone
    """
    try:
        # Greenpoint coordinates
        url = "https://api.weather.gov/points/40.7313,-73.9542"
        response = requests.get(url, headers={"User-Agent": "MTA Display App"}, timeout=5)
        data = response.json()
        forecast_url = data['properties']['forecast']
        hourly_url = data['properties']['forecastHourly']

        # Get sunrise/sunset times first to determine if it's day or night
        from dateutil import parser
        import pytz
        from datetime import timedelta

        eastern = pytz.timezone('America/New_York')
        now_local = datetime.now(eastern)

        forecast = requests.get(forecast_url, headers={"User-Agent": "MTA Display App"}, timeout=5)
        periods = forecast.json()['properties']['periods']

        # Fetch hourly forecast and filter to next 8 hours from now
        hourly_response = requests.get(hourly_url, headers={"User-Agent": "MTA Display App"}, timeout=5)
        all_hourly_periods = hourly_response.json()['properties']['periods']

        # Filter periods to only include future hours
        hourly_periods = []
        for period in all_hourly_periods:
            period_start = parser.parse(period['startTime']).astimezone(eastern)
            # Only include periods that are in the future or current hour
            if period_start >= now_local - timedelta(minutes=30):  # Include current hour (within 30 min)
                hourly_periods.append(period)
                if len(hourly_periods) >= 12:
                    break

        sun_url = "https://api.sunrise-sunset.org/json?lat=40.7313&lng=-73.9542&formatted=0"
        sun_response = requests.get(sun_url, timeout=5)
        sun_data = sun_response.json()['results']

        sunrise_utc = parser.parse(sun_data['sunrise'])
        sunset_utc = parser.parse(sun_data['sunset'])
        sunrise_local = sunrise_utc.astimezone(eastern)
        sunset_local = sunset_utc.astimezone(eastern)

        # Determine if it's currently daytime or nighttime
        is_daytime = sunrise_local <= now_local < sunset_local

        # Find the first period matching current day/night status
        current = None
        for period in periods:
            if period['isDaytime'] == is_daytime:
                current = period
                break

        # Fallback to first period if no match found
        if current is None:
            current = periods[0]

        temp = current['temperature']
        condition = current['shortForecast']

        # Get the weather icon before shortening text
        main_icon = get_weather_icon(condition)

        # Shorten common conditions
        condition_short = condition.replace("Mostly", "M.").replace("Partly", "P.")
        condition_short = condition_short.replace("Cloudy", "Cloudy").replace("Sunny", "Sunny")

        # Limit length to prevent cutoff
        if len(condition_short) > 15:
            condition_short = condition_short[:15]

        # Determine which upcoming sun event to show (sunrise/sunset data already fetched above)
        if now_local < sunrise_local:
            # Before sunrise - show today's sunrise
            sun_time = sunrise_local.strftime('%I:%M %p').lstrip('0')
            sun_icon = 'sunrise'
        elif now_local < sunset_local:
            # After sunrise but before sunset - show today's sunset
            sun_time = sunset_local.strftime('%I:%M %p').lstrip('0')
            sun_icon = 'sunset'
        else:
            # After sunset - show tomorrow's sunrise
            tomorrow = now_local.date() + timedelta(days=1)
            sun_url_tomorrow = f"https://api.sunrise-sunset.org/json?lat=40.7313&lng=-73.9542&formatted=0&date={tomorrow}"
            sun_response_tomorrow = requests.get(sun_url_tomorrow, timeout=5)
            sun_data_tomorrow = sun_response_tomorrow.json()['results']
            sunrise_utc_tomorrow = parser.parse(sun_data_tomorrow['sunrise'])
            sunrise_local_tomorrow = sunrise_utc_tomorrow.astimezone(eastern)
            sun_time = sunrise_local_tomorrow.strftime('%I:%M %p').lstrip('0')
            sun_icon = 'sunrise'

        weather_text = f"{temp}°F {condition_short}"

        # Format hourly forecast for display
        from dateutil import parser
        hourly_forecast = []
        for i, period in enumerate(hourly_periods):
            # Parse the time from the period
            start_time = parser.parse(period['startTime']).astimezone(eastern)

            # Check if this is the current hour
            if i == 0 and start_time.hour == now_local.hour:
                time_label = "NOW"
            else:
                # Format as hour (e.g., "3 PM", "1 AM")
                time_label = start_time.strftime('%I %p').lstrip('0')

            hourly_forecast.append({
                'time': time_label,
                'temp': period['temperature'],
                'condition': period['shortForecast'],
                'hour_time': start_time  # Store datetime for day/night checking
            })

        return (weather_text, main_icon, sun_icon, sun_time, hourly_forecast, sunrise_local, sunset_local)
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return ("", "partly-cloudy", "sunrise", "", [], None, None)


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
            small_font = ImageFont.truetype(font_paths['bold'], 32 * SCALE, index=1)
        else:
            # Linux or separate font files (.ttf) - no index parameter
            # Note: On Linux with .ttc, we load it without index (may not get true bold)
            print(f"Loading fonts without index parameter (Linux or .ttf files)")
            print(f"Bold font path: {font_paths['bold']}, size: {36 * SCALE}")
            header_font = ImageFont.truetype(font_paths['bold'], 26 * SCALE)
            line_font = ImageFont.truetype(font_paths['bold'], 48 * SCALE)
            dest_font = ImageFont.truetype(font_paths['bold'], 48 * SCALE)
            time_font = ImageFont.truetype(font_paths['bold'], 40 * SCALE)
            small_font = ImageFont.truetype(font_paths['bold'], 23 * SCALE)
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
    footer_height = 250
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
        circle_radius = 32 * SCALE
        draw_antialiased_circle(img, circle_x, circle_y, circle_radius,
                               LINE_COLOR, "G", line_font, font_index=1, use_font_index=use_font_index)

        # Draw destination
        draw.text((140 * SCALE, y_pos + 18), destination, fill=TEXT_COLOR, font=dest_font)

        # Draw arrival time - center-aligned at a fixed x position
        time_text = str(minutes) if minutes > 0 else "Now"
        # Fixed x position for center of time numbers (about 100px from right edge)
        time_center_x = SCALED_WIDTH - 62 * SCALE

        if minutes > 0:
            draw.text((time_center_x, y_pos + 22 * SCALE), time_text, fill=TEXT_COLOR, font=time_font, anchor='mm')
        else:
            draw.text((SCALED_WIDTH - 85 * SCALE, y_pos + 32 * SCALE), time_text, fill=TEXT_COLOR, font=time_font, anchor='mm')

        # Draw "min" label if not "Now" - center-aligned below the number
        if minutes > 0:
            draw.text((time_center_x, y_pos + 55 * SCALE), "MIN", fill=TEXT_COLOR, font=small_font, anchor='mm')

        y_pos += line_height

        # Draw dark separator line between trains (not after the last one)
        if idx < len(all_trains) - 1:
            # Separator goes exactly at the row boundary
            line_y = (idx + 1) * line_height
            draw.line([(0, line_y), (SCALED_WIDTH, line_y)],
                     fill=SEPARATOR_COLOR, width=8 * SCALE)

    # Draw thin footer at bottom with time in bottom left
    footer_height_scaled = footer_height * SCALE
    draw.rectangle([0, SCALED_HEIGHT - footer_height_scaled, SCALED_WIDTH, SCALED_HEIGHT], fill=HEADER_BG)

    # Draw bottom time bar with different color
    time_bar_height = 50 * SCALE
    draw.rectangle([0, SCALED_HEIGHT - time_bar_height, SCALED_WIDTH, SCALED_HEIGHT], fill=TIME_BAR_BG)

    # Add current time in bottom left corner
    current_time = datetime.now().strftime("%I:%M %p")
    draw.text((20 * SCALE, SCALED_HEIGHT - 35 * SCALE), current_time, fill=HEADER_TEXT, font=small_font)

    # Add weather in bottom right corner with icons
    weather_data = get_weather()
    if weather_data and weather_data[0]:  # Check if weather_text is not empty
        weather_text, main_icon, sun_icon, sun_time, hourly_forecast, sunrise_local, sunset_local = weather_data

        # Get icon directory path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_dir = os.path.join(script_dir, "icons")

        # Render weather icons at 2x scale
        icon_size = 30 * SCALE  # Icon size in scaled pixels

        # Load main weather icon (pre-converted to white PNG)
        main_icon_path = os.path.join(icon_dir, f"{main_icon}.png")
        main_icon_img = load_png_icon(main_icon_path, icon_size)

        # Load sun icon (pre-converted to white PNG)
        sun_icon_path = os.path.join(icon_dir, f"{sun_icon}.png")
        sun_icon_img = load_png_icon(sun_icon_path, icon_size)

        # Calculate positions from right edge
        margin = 20 * SCALE
        icon_spacing = 8 * SCALE

        # Measure text widths
        weather_bbox = draw.textbbox((0, 0), weather_text, font=small_font)
        weather_width = weather_bbox[2] - weather_bbox[0]

        sun_time_bbox = draw.textbbox((0, 0), sun_time, font=small_font)
        sun_time_width = sun_time_bbox[2] - sun_time_bbox[0]

        # Layout from right to left: sun_time + sun_icon + spacing + weather_text + main_icon
        total_width = (sun_time_width + icon_spacing + icon_size +
                      icon_spacing * 2 + weather_width + icon_spacing + icon_size)

        # Starting x position
        start_x = SCALED_WIDTH - total_width - margin

        # Draw main weather icon
        y_icon = SCALED_HEIGHT - 38 * SCALE #(footer_height_scaled - icon_size) // 2 
        #img.paste(main_icon_img, (start_x, y_icon), main_icon_img)

        # Draw weather text
        text_x = start_x + icon_size + icon_spacing
        text_y = SCALED_HEIGHT - 35 * SCALE
        #draw.text((text_x, text_y), weather_text, fill=HEADER_TEXT, font=small_font)

        # Draw sun icon
        sun_icon_x = text_x + weather_width + icon_spacing * 2
        img.paste(sun_icon_img, (sun_icon_x, y_icon), sun_icon_img)

        # Draw sun time
        sun_time_x = sun_icon_x + icon_size + icon_spacing
        draw.text((sun_time_x, text_y), sun_time, fill=HEADER_TEXT, font=small_font)

        # Draw 8-hour forecast horizontally in the center of the footer
        if hourly_forecast:
            # Create a smaller font for hourly forecast (use regular, not bold)
            try:
                if use_font_index:
                    hourly_time_font = ImageFont.truetype(font_paths['regular'], 18 * SCALE, index=0)
                    hourly_temp_font = ImageFont.truetype(font_paths['bold'], 24 * SCALE, index=0)
                else:
                    hourly_time_font = ImageFont.truetype(font_paths['regular'], 18 * SCALE)
                    hourly_temp_font = ImageFont.truetype(font_paths['bold'], 22 * SCALE)
            except:
                hourly_time_font = small_font
                hourly_temp_font = header_font

            # Calculate available space for hourly forecast
            # Place it in the middle section of the footer
            left_margin = 20 * SCALE
            right_margin = SCALED_WIDTH - 20 * SCALE
            forecast_width = right_margin - left_margin

            # Calculate spacing for hours
            num_hours = len(hourly_forecast)
            hour_spacing = forecast_width // num_hours

            # Find min and max temperatures for scaling
            temps = [hour_data['temp'] for hour_data in hourly_forecast]
            min_temp = min(temps)
            max_temp = max(temps)
            temp_range = max_temp - min_temp if max_temp > min_temp else 1

            # Y positions for the hourly forecast
            forecast_y_time = SCALED_HEIGHT - 85 * SCALE  # Time labels at bottom
            # Available vertical space for temperature graph (between weather info and time labels)
            graph_top = SCALED_HEIGHT - footer_height_scaled + 20 * SCALE
            graph_bottom = SCALED_HEIGHT - 165 * SCALE
            graph_height = graph_bottom - graph_top

            # Draw each hour
            for i, hour_data in enumerate(hourly_forecast):
                x_pos = left_margin + i * hour_spacing + hour_spacing // 2

                # Determine if this hour is during day or night
                hour_time = hour_data.get('hour_time')  # This should be a datetime object
                is_night = hour_time and (hour_time < sunrise_local or hour_time >= sunset_local)

                # Get weather icon for this hour
                condition_icon = get_weather_icon(hour_data['condition'])

                # Override with night icons if it's nighttime
                if is_night:
                    if 'clear' in condition_icon or 'sunny' in condition_icon:
                        condition_icon = 'clear-night'
                    elif 'partly-cloudy' in condition_icon:
                        condition_icon = 'partly-cloudy'  # Could add a night variant if you have one
                    elif 'cloudy' in condition_icon:
                        condition_icon = 'cloudy'  # Cloudy looks the same day or night

                icon_path = os.path.join(icon_dir, f"{condition_icon}.png")
                hourly_icon_size = 28 * SCALE
                hourly_icon_img = load_png_icon(icon_path, hourly_icon_size)

                # Draw weather icon above time label
                icon_y = SCALED_HEIGHT - 120 * SCALE
                img.paste(hourly_icon_img, (x_pos - hourly_icon_size // 2, icon_y), hourly_icon_img)

                # Draw time label at fixed position at bottom
                time_text = hour_data['time']
                time_bbox = draw.textbbox((0, 0), time_text, font=hourly_time_font)
                time_width = time_bbox[2] - time_bbox[0]
                draw.text((x_pos - time_width // 2, forecast_y_time),
                         time_text, fill=HEADER_TEXT, font=hourly_time_font)

                # Draw temperature at Y position based on temperature value
                # Higher temp = higher up (lower Y value)
                temp = hour_data['temp']
                # Normalize temperature to 0-1 range
                if temp_range > 0:
                    normalized_temp = (temp - min_temp) / temp_range
                else:
                    normalized_temp = 0.5

                # Map to Y position (invert because higher Y is lower on screen)
                temp_y = graph_bottom - (normalized_temp * graph_height)

                temp_text = f"{temp}°"
                temp_bbox = draw.textbbox((0, 0), temp_text, font=hourly_temp_font)
                temp_width = temp_bbox[2] - temp_bbox[0]
                temp_height = temp_bbox[3] - temp_bbox[1]
                draw.text((x_pos - temp_width // 2, temp_y),
                         temp_text, fill=HEADER_TEXT, font=hourly_temp_font)

                # Draw thin line from just above icon to just below temperature
                line_start_y = icon_y - 5 * SCALE  # Just above icon
                line_end_y = temp_y + temp_height + 10 * SCALE  # Just below temperature
                draw.line([(x_pos, line_start_y), (x_pos, line_end_y)],
                         fill=WEATHER_LINE, width=3 * SCALE)

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
