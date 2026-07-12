import serial
import sys
import time

if len(sys.argv) > 1:
    COM_PORT = sys.argv[1]
else:
    COM_PORT = 'COM3'

try:
    ser = serial.Serial(port=COM_PORT, baudrate=921600, timeout=1)
    
    # Send Start Acquisition
    packet = bytearray([0x08, 0x83, 0x88])
    ser.write(packet)
    
    print("Reading raw bytes. Touch the sensors...")
    
    # Read until a marker \xA0 is found
    while True:
        if ser.read(1) == b"\xA0":
            chunk = ser.read(45)
            # Print the whole chunk in hex
            print(chunk.hex())
            time.sleep(0.1)
            
except KeyboardInterrupt:
    print("Stopped.")
    ser.close()
except Exception as e:
    print(f"Error: {e}")
