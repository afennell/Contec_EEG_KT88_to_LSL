import serial
import struct
import pylsl
import time

COM_PORT = "COM3"
BAUD_RATE = 921600      # Start with 115200; if wrong, try 460800 or 256000
CHANNEL_COUNT = 16
FRAME_SIZE = CHANNEL_COUNT * 2  # int16 per channel

# -------------------------
# OPEN SERIAL PORT
# -------------------------

ser = serial.Serial(
    port=COM_PORT,
    baudrate=BAUD_RATE,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=0.1
)

print("Sending start-stream command...")
ser.write(b'\x08')
ser.write(b'\x83')
ser.write(b'\x88')

time.sleep(0.1)
print("Start-stream command sent.")

# -------------------------
# LSL SETUP
# -------------------------

info = pylsl.StreamInfo(
    name="KT88_1016",
    type="EEG",
    channel_count=CHANNEL_COUNT,
    nominal_srate=100,
    channel_format="float32",
    source_id="contec_kt88_1016"
)
outlet = pylsl.StreamOutlet(info)

print("Streaming…")

# -------------------------
# READ LOOP
# -------------------------

# -------------------------
# SCALING FACTOR
# -------------------------
SCALING_FACTOR = 0.1

def decode(frame):
    vals = struct.unpack("<" + "h"*CHANNEL_COUNT, frame)
    return [v * SCALING_FACTOR for v in vals]  # approximate uV scaling
try:
    while True:
        frame = ser.read(FRAME_SIZE)

        if len(frame) != FRAME_SIZE:
            continue

        sample = decode(frame)
        outlet.push_sample(sample)

except KeyboardInterrupt:
    print("Ctrl+C pressed, sending command...")
    ser.write(b'\xFF')   # send your command
    ser.flush()
finally:
    ser.close()
