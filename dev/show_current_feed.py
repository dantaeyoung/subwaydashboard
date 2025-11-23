#!/usr/bin/env python3
"""Show exactly what's in the current ferry feed"""

import requests
from google.transit import gtfs_realtime_pb2
from datetime import datetime
from collections import defaultdict

response = requests.get("http://nycferry.connexionz.net/rtt/public/utility/gtfsrealtime.aspx/tripupdate", timeout=10)
feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(response.content)

print(f"Feed timestamp: {datetime.fromtimestamp(feed.header.timestamp)}")
print(f"Total trips: {len(feed.entity)}\n")

# Group stops by trip to see routes
trips_info = []

for entity in feed.entity:
    if entity.HasField('trip_update'):
        trip = entity.trip_update
        trip_id = trip.trip.trip_id if trip.trip.HasField('trip_id') else "Unknown"
        route_id = trip.trip.route_id if trip.trip.HasField('route_id') else "Unknown"

        stops = []
        for stop_time in sorted(trip.stop_time_update, key=lambda x: x.stop_sequence if x.HasField('stop_sequence') else 0):
            stop_id = stop_time.stop_id
            seq = stop_time.stop_sequence if stop_time.HasField('stop_sequence') else '?'

            time_str = ""
            if stop_time.HasField('arrival'):
                arr_time = datetime.fromtimestamp(stop_time.arrival.time)
                time_str = arr_time.strftime("%H:%M")
            elif stop_time.HasField('departure'):
                dep_time = datetime.fromtimestamp(stop_time.departure.time)
                time_str = dep_time.strftime("%H:%M")

            stops.append(f"{stop_id}@{time_str}")

        trips_info.append({
            'trip_id': trip_id,
            'route_id': route_id,
            'stops': stops,
            'num_stops': len(stops)
        })

# Sort by number of stops (longer routes first)
trips_info.sort(key=lambda x: x['num_stops'], reverse=True)

print("All trips in current feed:")
print("="*80)
for i, trip in enumerate(trips_info, 1):
    print(f"\n{i}. Trip {trip['trip_id']} (Route: {trip['route_id']}, {trip['num_stops']} stops)")
    print(f"   Route: {' → '.join(trip['stops'])}")

# Show unique stops
all_stops = set()
for trip in trips_info:
    for stop in trip['stops']:
        stop_id = stop.split('@')[0]
        all_stops.add(stop_id)

print(f"\n{'='*80}")
print(f"Unique stops in feed: {sorted(all_stops, key=lambda x: int(x) if x.isdigit() else 0)}")
print(f"Total unique stops: {len(all_stops)}")
