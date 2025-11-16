#!/usr/bin/env python3
"""Comprehensive analysis of ferry feed"""

import requests
from google.transit import gtfs_realtime_pb2
from datetime import datetime

response = requests.get("http://nycferry.connexionz.net/rtt/public/utility/gtfsrealtime.aspx/tripupdate", timeout=10)
feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(response.content)

print(f"Feed timestamp: {datetime.fromtimestamp(feed.header.timestamp)}")
print(f"Total entities: {len(feed.entity)}\n")

# Analyze first few entities in detail
for i, entity in enumerate(feed.entity[:5]):
    print(f"{'='*60}")
    print(f"Entity {i+1}: {entity.id}")
    print(f"{'='*60}")

    if entity.HasField('trip_update'):
        trip = entity.trip_update
        print(f"Trip ID: {trip.trip.trip_id if trip.trip.HasField('trip_id') else 'N/A'}")
        print(f"Route ID: {trip.trip.route_id if trip.trip.HasField('route_id') else 'N/A'}")
        print(f"Direction ID: {trip.trip.direction_id if trip.trip.HasField('direction_id') else 'N/A'}")
        print(f"Start time: {trip.trip.start_time if trip.trip.HasField('start_time') else 'N/A'}")
        print(f"Start date: {trip.trip.start_date if trip.trip.HasField('start_date') else 'N/A'}")
        print(f"Number of stop updates: {len(trip.stop_time_update)}")

        print("\nStop updates:")
        for stop_update in trip.stop_time_update:
            stop_id = stop_update.stop_id
            seq = stop_update.stop_sequence if stop_update.HasField('stop_sequence') else 'N/A'

            if stop_update.HasField('arrival'):
                arr_time = datetime.fromtimestamp(stop_update.arrival.time)
                arr_delay = stop_update.arrival.delay if stop_update.arrival.HasField('delay') else 0
            else:
                arr_time = 'N/A'
                arr_delay = 0

            if stop_update.HasField('departure'):
                dep_time = datetime.fromtimestamp(stop_update.departure.time)
            else:
                dep_time = 'N/A'

            print(f"  Stop {stop_id} (seq={seq}): arr={arr_time}, dep={dep_time}, delay={arr_delay}s")

    print()

# Summary of all stops across all trips
print(f"\n{'='*60}")
print("SUMMARY OF ALL TRIPS")
print(f"{'='*60}")

trips_by_stop_count = {}
all_stop_ids = set()

for entity in feed.entity:
    if entity.HasField('trip_update'):
        trip = entity.trip_update
        num_stops = len(trip.stop_time_update)
        trips_by_stop_count[num_stops] = trips_by_stop_count.get(num_stops, 0) + 1

        for stop_update in trip.stop_time_update:
            all_stop_ids.add(stop_update.stop_id)

print(f"\nTrips by number of stops:")
for num_stops in sorted(trips_by_stop_count.keys()):
    print(f"  {num_stops} stops: {trips_by_stop_count[num_stops]} trips")

print(f"\nAll unique stop IDs ({len(all_stop_ids)} total):")
print(f"  {sorted(all_stop_ids, key=lambda x: int(x) if x.isdigit() else 0)}")

# Find trips with multiple stops (actual routes, not just current position)
print(f"\n{'='*60}")
print("MULTI-STOP TRIPS (Actual Routes)")
print(f"{'='*60}")

for entity in feed.entity:
    if entity.HasField('trip_update'):
        trip = entity.trip_update
        if len(trip.stop_time_update) > 3:  # Only show trips with more than 3 stops
            trip_id = trip.trip.trip_id if trip.trip.HasField('trip_id') else 'Unknown'
            route_id = trip.trip.route_id if trip.trip.HasField('route_id') else 'Unknown'
            stops = [s.stop_id for s in sorted(trip.stop_time_update, key=lambda x: x.stop_sequence if x.HasField('stop_sequence') else 0)]
            print(f"\nTrip {trip_id} (Route: {route_id})")
            print(f"  Stops: {' -> '.join(stops)}")
