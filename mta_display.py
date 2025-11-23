#!/usr/bin/env python3
"""
MTA G Train Display Generator
Creates an 800x600 PNG showing next trains at Greenpoint G station
"""

from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from nyct_gtfs import NYCTFeed

# Station IDs
G_TRAIN_GREENPOINT_NORTH = "G26N"  # Queens-bound
G_TRAIN_GREENPOINT_SOUTH = "G26S"  # Church Ave-bound

# Display settings
WIDTH = 800
HEIGHT = 600
BG_COLOR = (106, 115, 122)  # Blue background
TEXT_COLOR = (255, 255, 255)  # White text
LINE_COLOR = (131, 190, 82)  # G train green color
SEPARATOR_COLOR = (30, 30, 30)  # Dark blue separator
HEADER_BG = (30, 30, 30)  # Dark gray footer background
HEADER_TEXT = (255, 255, 255)  # White header text


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


def draw_antialiased_circle(img, center_x, center_y, radius, fill_color, text, text_font):
    """Draw an antialiased circle with centered text"""
    # Create a high-resolution temporary image (4x scale for better antialiasing)
    scale = 4
    size = radius * 2 * scale
    circle_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    circle_draw = ImageDraw.Draw(circle_img)

    # Draw circle at high resolution
    circle_draw.ellipse([0, 0, size, size], fill=fill_color)

    # Draw text at high resolution - scale up the font
    scaled_font = ImageFont.truetype(text_font.path, text_font.size * scale)
    # Use anchor='mm' to center text at the middle
    circle_draw.text((size // 2, size // 2), text, fill=(255, 255, 255),
                    font=scaled_font, anchor='mm')

    # Resize down with high-quality antialiasing
    circle_img = circle_img.resize((radius * 2, radius * 2), Image.Resampling.LANCZOS)

    # Paste onto main image
    img.paste(circle_img, (center_x - radius, center_y - radius), circle_img)


def create_display_image(output_path="schedule.png"):
    """Create the MTA display image"""

    # Create image at 2x resolution for better text antialiasing
    SCALE = 2
    SCALED_WIDTH = WIDTH * SCALE
    SCALED_HEIGHT = HEIGHT * SCALE

    img = Image.new('RGB', (SCALED_WIDTH, SCALED_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Use Helvetica fonts at 2x size
    try:
        # Bold fonts for most text
        header_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36 * SCALE, index=1)  # Bold
        line_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 62 * SCALE, index=1)  # Bold
        dest_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 55 * SCALE, index=1)  # Bold
        # Regular fonts for time numbers and "min"
        time_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60 * SCALE, index=1)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22 * SCALE)
    except:
        # Fallback to default font if Helvetica is not available
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
                               LINE_COLOR, "G", line_font)

        # Draw destination
        draw.text((140 * SCALE, y_pos + 10), destination, fill=TEXT_COLOR, font=dest_font)

        # Draw arrival time
        time_text = str(minutes) if minutes > 0 else "Now"
        time_bbox = draw.textbbox((0, 0), time_text, font=time_font)
        time_width = time_bbox[2] - time_bbox[0]
        if minutes > 0:
            draw.text((SCALED_WIDTH - time_width - 40 * SCALE, y_pos - 10), time_text, fill=TEXT_COLOR, font=time_font)
        else:
            draw.text((SCALED_WIDTH - time_width - 40 * SCALE, y_pos + 5), time_text, fill=TEXT_COLOR, font=time_font)

        # Draw "min" label if not "Now" - align with proper right margin
        if minutes > 0:
            min_bbox = draw.textbbox((0, 0), "MIN", font=small_font)
            min_width = min_bbox[2] - min_bbox[0]
            draw.text((SCALED_WIDTH - min_width - 40 * SCALE, y_pos + 50 * SCALE), "MIN", fill=TEXT_COLOR, font=small_font)

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

    # Scale image down to target size for antialiasing
    img = img.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

    # Save image
    img.save(output_path)
    print(f"Image saved to {output_path}")


if __name__ == "__main__":
    create_display_image()
