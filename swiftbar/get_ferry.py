#!/Users/provolot/.pyenv/versions/3.10.15/bin/python3
"""Standalone script to get ferry arrival times - called by main script"""

import sys
import requests
from datetime import datetime
from google.transit import gtfs_realtime_pb2

FERRY_TRIP_UPDATES = "http://nycferry.connexionz.net/rtt/public/utility/gtfsrealtime.aspx/tripupdate"

try:
    response = requests.get(FERRY_TRIP_UPDATES, timeout=10)
    if response.status_code != 200:
        print("0")  # No arrivals
        sys.exit(0)

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)

    all_arrivals = []
    now = datetime.now().timestamp()

    for entity in feed.entity:
        if entity.HasField('trip_update'):
            trip = entity.trip_update

            for stop_time in trip.stop_time_update:
                if stop_time.stop_id == "18":  # Greenpoint stop
                    # Prefer departure time (when ferry leaves) over arrival time (when it arrives)
                    # If ferry is at the stop, departure is in the future and more useful
                    if stop_time.HasField('departure'):
                        arrival_time = stop_time.departure.time
                    elif stop_time.HasField('arrival'):
                        arrival_time = stop_time.arrival.time
                    else:
                        continue

                    minutes_away = int((arrival_time - now) / 60)
                    if minutes_away >= 0:
                        all_arrivals.append(minutes_away)

    # Sort and output as comma-separated values (next 3 arrivals)
    all_arrivals.sort()
    if all_arrivals:
        print(','.join(map(str, all_arrivals[:3])))
    else:
        print("")  # No arrivals - output empty string

except Exception as e:
    print("", file=sys.stderr)  # Error - return no arrivals
    sys.exit(1)
