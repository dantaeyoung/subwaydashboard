#!/usr/bin/env python3
"""Test if stop ID 18 (Greenpoint) appears in current ferry feed"""

import requests
from google.transit import gtfs_realtime_pb2
from datetime import datetime

response = requests.get("http://nycferry.connexionz.net/rtt/public/utility/gtfsrealtime.aspx/tripupdate", timeout=10)
feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(response.content)

print(f"Feed timestamp: {datetime.fromtimestamp(feed.header.timestamp)}")
print(f"Total entities: {len(feed.entity)}\n")

# Check all stop IDs
all_stops = set()
stop_18_found = False

for entity in feed.entity:
    if entity.HasField('trip_update'):
        trip = entity.trip_update
        for stop_time in trip.stop_time_update:
            all_stops.add(stop_time.stop_id)
            if stop_time.stop_id == "18":
                stop_18_found = True
                print(f"✅ FOUND STOP 18 in trip {trip.trip.trip_id if trip.trip.HasField('trip_id') else 'Unknown'}")
                if stop_time.HasField('arrival'):
                    arr_time = datetime.fromtimestamp(stop_time.arrival.time)
                    print(f"   Arrival: {arr_time}")
                if stop_time.HasField('departure'):
                    dep_time = datetime.fromtimestamp(stop_time.departure.time)
                    print(f"   Departure: {dep_time}")
                print()

if not stop_18_found:
    print("❌ Stop ID 18 (Greenpoint) NOT found in current feed")
    print(f"\nAll stop IDs currently in feed ({len(all_stops)} total):")
    print(sorted(all_stops, key=lambda x: int(x) if x.isdigit() else 0))
else:
    print(f"\n✅ Stop 18 is in the feed!")
