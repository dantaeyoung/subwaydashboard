#!/usr/bin/env python3
"""Debug the ferry function to see what's happening"""

import requests
from datetime import datetime
from google.transit import gtfs_realtime_pb2

FERRY_TRIP_UPDATES = "http://nycferry.connexionz.net/rtt/public/utility/gtfsrealtime.aspx/tripupdate"

response = requests.get(FERRY_TRIP_UPDATES, timeout=10)
print(f"Response status: {response.status_code}")

if response.status_code != 200:
    print("Failed to get ferry data")
    exit(1)

feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(response.content)

all_arrivals = []
now = datetime.now().timestamp()

print(f"Current time: {datetime.fromtimestamp(now)}")
print(f"Looking for stop ID: '18'\n")

for entity in feed.entity:
    if entity.HasField('trip_update'):
        trip = entity.trip_update
        trip_id = trip.trip.trip_id if trip.trip.HasField('trip_id') else ""

        for stop_time in trip.stop_time_update:
            print(f"Checking stop: '{stop_time.stop_id}' (type: {type(stop_time.stop_id)})")

            # Check if this is the Greenpoint stop (ID: 18)
            if stop_time.stop_id == "18":
                print(f"  ✅ MATCH! Found stop 18 in trip {trip_id}")

                if stop_time.HasField('arrival'):
                    arrival_time = stop_time.arrival.time
                    print(f"  Has arrival time: {datetime.fromtimestamp(arrival_time)}")
                elif stop_time.HasField('departure'):
                    arrival_time = stop_time.departure.time
                    print(f"  Has departure time: {datetime.fromtimestamp(arrival_time)}")
                else:
                    print(f"  No arrival or departure time")
                    continue

                minutes_away = int((arrival_time - now) / 60)
                print(f"  Minutes away: {minutes_away}")

                if minutes_away >= 0:
                    all_arrivals.append({
                        'minutes': minutes_away,
                        'trip_id': trip_id
                    })
                    print(f"  Added to arrivals list")
                else:
                    print(f"  Skipped (negative time)")

print(f"\n{'='*60}")
print(f"Total arrivals found: {len(all_arrivals)}")
print(f"Arrivals: {all_arrivals}")
