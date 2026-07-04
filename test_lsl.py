from pylsl import resolve_streams
import time

print("Scanning for LSL streams...")
streams = resolve_streams(wait_time=5)
for s in streams:
    print(f"Name: {s.name()}, Type: {s.type()}")
