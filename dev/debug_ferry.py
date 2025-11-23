#!/usr/bin/env python3
"""Debug script to test Ferry API only"""

import requests
from datetime import datetime
from google.transit import gtfs_realtime_pb2

print("=" * 60)
print("TESTING NYC FERRY API")
print("=" * 60)

try:
    response = requests.get("http://nycferry.connexionz.net/rtt/public/utility/gtfsrealtime.aspx/tripupdate", timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content Length: {len(response.content)} bytes")

    if response.status_code == 200:
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)

        print(f"\nFeed Entities: {len(feed.entity)}")

        # Find all unique stop IDs and trip info
        stop_ids = set()
        trip_info = []

        for entity in feed.entity:
            if entity.HasField('trip_update'):
                trip = entity.trip_update
                trip_id = trip.trip.trip_id if trip.trip.HasField('trip_id') else "No trip_id"
                route_id = trip.trip.route_id if trip.trip.HasField('route_id') else "No route"

                for stop_time in trip.stop_time_update:
                    stop_ids.add(stop_time.stop_id)
                    trip_info.append({
                        'stop_id': stop_time.stop_id,
                        'trip_id': trip_id,
                        'route': route_id
                    })

        print(f"\nAll Stop IDs in feed: {len(stop_ids)} unique stops")
        print(f"Stop IDs: {sorted(stop_ids)}")

        # Find Greenpoint-related stops
        greenpoint_stops = [sid for sid in stop_ids if 'gre' in sid.lower() or 'greenpoint' in sid.lower() or 'india' in sid.lower()]
        print(f"\nGreenpoint-related stops: {greenpoint_stops}")

        # Show all trip info for Greenpoint
        print("\nAll trips with Greenpoint/India stops:")
        greenpoint_trips = [info for info in trip_info if any(term in info['stop_id'].lower() for term in ['gre', 'greenpoint', 'india'])]
        for info in greenpoint_trips[:20]:
            print(f"  Stop: {info['stop_id']}, Trip: {info['trip_id']}, Route: {info['route']}")

        # Show sample arrivals
        if greenpoint_stops:
            print(f"\nSample arrivals for stop: {greenpoint_stops[0]}")
            now = datetime.now().timestamp()
            count = 0
            for entity in feed.entity:
                if entity.HasField('trip_update'):
                    trip = entity.trip_update
                    trip_id = trip.trip.trip_id if trip.trip.HasField('trip_id') else "No trip_id"
                    for stop_time in trip.stop_time_update:
                        if stop_time.stop_id == greenpoint_stops[0]:
                            if stop_time.HasField('arrival'):
                                arrival_time = stop_time.arrival.time
                                minutes_away = int((arrival_time - now) / 60)
                                print(f"  Trip {trip_id}: Arrival in {minutes_away}min")
                                count += 1
            if count == 0:
                print("  No arrivals found")

except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
