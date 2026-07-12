import pylsl
import time
import sys

# Create an LSL marker stream
info = pylsl.StreamInfo(name="Markers_Contec", type="Markers", channel_count=1, nominal_srate=0, channel_format="string", source_id="markers_123")
outlet = pylsl.StreamOutlet(info)

print("Marker Processor - LSL Marker Stream Handler")
print("=" * 50)
print("Marker stream created: 'Markers_Contec'")
print("Commands:")
print("  - Type a marker name to send (e.g., 'Left', 'Right', 'Rest')")
print("  - Press Enter to send")
print("  - Press Ctrl+C to stop")
print("=" * 50)

try:
    while True:
        marker = input("\nEnter marker: ").strip()
        if marker:
            outlet.push_sample([marker])
            print(f"✓ Sent: '{marker}'")
except KeyboardInterrupt:
    print("\n\nMarker processor stopped.")
