#!/Users/provolot/.pyenv/versions/3.10.15/bin/python3
# <xbar.title>Greenpoint Transit</xbar.title>
# <xbar.version>v1.0</xbar.version>
# <xbar.author>Claude</xbar.author>
# <xbar.author.github>anthropics</xbar.author.github>
# <xbar.desc>Shows real-time G train and NYC Ferry schedules for Greenpoint</xbar.desc>
# <xbar.dependencies>python3</xbar.dependencies>

import sys
import os
import subprocess
from datetime import datetime
from nyct_gtfs import NYCTFeed

# Station IDs
G_TRAIN_GREENPOINT_NORTH = "G26N"  # Queens-bound
G_TRAIN_GREENPOINT_SOUTH = "G26S"  # Church Ave-bound

def get_mta_arrivals(stop_id):
    """Get next arrivals for a specific MTA stop using nyct-gtfs library"""
    try:
        feed = NYCTFeed("G")
        trains = feed.trips  # Get all trips

        arrivals = []
        now = datetime.now()

        for train in trains:
            # Check if this train stops at our station
            for stop_update in train.stop_time_updates:
                if stop_update.stop_id == stop_id and stop_update.arrival:
                    minutes_away = int((stop_update.arrival - now).total_seconds() / 60)
                    if minutes_away >= 0:  # Only future arrivals
                        arrivals.append(minutes_away)
                    break  # Found our stop, move to next train

        return sorted(arrivals)[:3]
    except Exception as e:
        return []

def get_ferry_arrivals():
    """Get next ferry arrivals for Greenpoint (stop ID: 18)

    Uses subprocess to avoid protobuf conflicts with nyct_gtfs
    """
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ferry_script = os.path.join(script_dir, "get_ferry.py")

        # Call the ferry script with the same Python interpreter
        result = subprocess.run(
            ["/Users/provolot/.pyenv/versions/3.10.15/bin/python3", ferry_script],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return {"hunters_point": [], "wall_st": []}

        output = result.stdout.strip()
        if not output:
            # No arrivals (empty string)
            return {"hunters_point": [], "wall_st": []}

        # Parse comma-separated arrival times
        arrivals = [int(x) for x in output.split(',') if x.strip()]

        # For now, show all ferries - we'll determine direction later
        return {
            "hunters_point": arrivals,  # Show all ferries here for now
            "wall_st": []  # Leave empty until we can determine direction
        }
    except Exception as e:
        return {"hunters_point": [], "wall_st": []}

def format_times(times):
    """Format arrival times for display"""
    if not times:
        return "No data"
    return ", ".join([f"{t}min" if t > 0 else "Now" for t in times])

def main():
    # Get all arrivals
    g_queens = get_mta_arrivals(G_TRAIN_GREENPOINT_NORTH)
    g_church = get_mta_arrivals(G_TRAIN_GREENPOINT_SOUTH)
    ferry = get_ferry_arrivals()

    # Menu bar - show soonest arrival
    soonest = []
    if g_queens:
        soonest.append(("G→Queens", g_queens[0]))
    if g_church:
        soonest.append(("G→Church", g_church[0]))
    if ferry["hunters_point"]:
        soonest.append(("Ferry→HP", ferry["hunters_point"][0]))
    if ferry["wall_st"]:
        soonest.append(("Ferry→WS", ferry["wall_st"][0]))

    # Menu bar - just show a simple icon
    print("🚇")

    # Separator for dropdown
    print("---")

    # Dropdown menu - show all routes
    print("🚊 G Train - Greenpoint Ave")
    print(f"  Queens-bound: {format_times(g_queens)} | font=monospace")
    print(f"  Church Ave-bound: {format_times(g_church)} | font=monospace")

    print("---")

    print("⛴️ East River Ferry - Greenpoint")
    print(f"  Hunters Point: {format_times(ferry['hunters_point'])} | font=monospace")
    print(f"  Wall St: {format_times(ferry['wall_st'])} | font=monospace")

    print("---")
    print(f"Updated: {datetime.now().strftime('%I:%M:%S %p')} | font=monospace size=10")

if __name__ == "__main__":
    main()
