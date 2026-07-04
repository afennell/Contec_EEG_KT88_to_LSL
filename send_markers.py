import pylsl
import time
import sys

# Create an LSL marker stream
info = pylsl.StreamInfo(name="Markers_Contec", type="Markers", channel_count=1, nominal_srate=0, channel_format="string", source_id="markers_123")
outlet = pylsl.StreamOutlet(info)

print("Marker stream created. Sending markers (e.g., 'arm_move', 'baseline')")
print("Press Ctrl+C to stop.")

try:
    while True:
        marker = input("Enter marker (e.g., arm_move, baseline): ")
        outlet.push_sample([marker])
        print(f"Sent: {marker}")
except KeyboardInterrupt:
    print("Stopped.")
