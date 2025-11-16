#!/usr/bin/env python3
"""Map ferry stop IDs to names by analyzing trip patterns"""

import requests
from google.transit import gtfs_realtime_pb2
from collections import defaultdict

print("Fetching ferry GTFS realtime feed...")
response = requests.get("http://nycferry.connexionz.net/rtt/public/utility/gtfsrealtime.aspx/tripupdate", timeout=10)

feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(response.content)

# Collect all stop sequences for each route
stop_sequences = defaultdict(list)

for entity in feed.entity:
    if entity.HasField('trip_update'):
        trip = entity.trip_update
        route_id = trip.trip.route_id if trip.trip.HasField('route_id') else "Unknown"

        # Get ordered list of stops for this trip
        stops_in_order = []
        for stop_time in sorted(trip.stop_time_update, key=lambda x: x.stop_sequence if x.HasField('stop_sequence') else 0):
            stops_in_order.append(stop_time.stop_id)

        if stops_in_order:
            stop_sequences[route_id].append(stops_in_order)

# Print routes and their stop patterns
for route_id, sequences in stop_sequences.items():
    print(f"\n{'='*60}")
    print(f"Route: {route_id}")
    print(f"{'='*60}")

    # Find most common sequence
    if sequences:
        first_sequence = sequences[0]
        print(f"Sample stop sequence: {' -> '.join(first_sequence)}")
        print(f"Number of stops: {len(first_sequence)}")
        print(f"Number of trips: {len(sequences)}")

print("\n" + "="*60)
print("All unique stop IDs found:")
print("="*60)
all_stops = set()
for sequences in stop_sequences.values():
    for seq in sequences:
        all_stops.update(seq)
print(sorted(all_stops, key=lambda x: int(x) if x.isdigit() else x))

# Based on known ferry routes, make educated guesses
print("\n" + "="*60)
print("ANALYSIS:")
print("="*60)
print("The East River route serves Greenpoint (India St) among other stops.")
print("Look for the 'ER' route above and identify which stop ID might be Greenpoint")
print("based on its position in the sequence.")
