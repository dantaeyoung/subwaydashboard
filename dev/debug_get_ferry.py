#!/usr/bin/env python3
"""Debug version of get_ferry.py with print statements"""

import sys
import requests
from datetime import datetime
from google.transit import gtfs_realtime_pb2

FERRY_TRIP_UPDATES = "http://nycferry.connexionz.net/rtt/public/utility/gtfsrealtime.aspx/tripupdate"

try:
    response = requests.get(FERRY_TRIP_UPDATES, timeout=10)
    print(f"Status: {response.status_code}", file=sys.stderr)

    if response.status_code != 200:
        print("0")
        sys.exit(0)

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)

    all_arrivals = []
    now = datetime.now().timestamp()
    print(f"Current time: {datetime.fromtimestamp(now)}", file=sys.stderr)

    for entity in feed.entity:
        if entity.HasField('trip_update'):
            trip = entity.trip_update

            for stop_time in trip.stop_time_update:
                if stop_time.stop_id == "18":
                    print(f"Found stop 18!", file=sys.stderr)

                    # Prefer departure over arrival
                    if stop_time.HasField('departure'):
                        arrival_time = stop_time.departure.time
                        print(f"Using departure time: {datetime.fromtimestamp(arrival_time)}", file=sys.stderr)
                    elif stop_time.HasField('arrival'):
                        arrival_time = stop_time.arrival.time
                        print(f"Using arrival time: {datetime.fromtimestamp(arrival_time)}", file=sys.stderr)
                    else:
                        print("No arrival or departure", file=sys.stderr)
                        continue

                    minutes_away = int((arrival_time - now) / 60)
                    print(f"Minutes away: {minutes_away}", file=sys.stderr)

                    if minutes_away >= 0:
                        all_arrivals.append(minutes_away)
                        print(f"Added to list", file=sys.stderr)
                    else:
                        print(f"Filtered out (negative time)", file=sys.stderr)

    print(f"All arrivals: {all_arrivals}", file=sys.stderr)

    # Sort and output
    all_arrivals.sort()
    if all_arrivals:
        output = ','.join(map(str, all_arrivals[:3]))
        print(f"Output: {output}", file=sys.stderr)
        print(output)
    else:
        print("No arrivals found", file=sys.stderr)
        print("0")

except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    print("0")
    sys.exit(1)
