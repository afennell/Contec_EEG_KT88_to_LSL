from pylsl import resolve_streams
import time

print("Looking for LSL streams...")
streams = resolve_streams(wait_time=5)
if len(streams) == 0:
    print("No streams found.")
else:
    print(f"Found {len(streams)} streams:")
    for s in streams:
        print(f"- Name: {s.name()}, Type: {s.type()}, Channel Count: {s.channel_count()}")
