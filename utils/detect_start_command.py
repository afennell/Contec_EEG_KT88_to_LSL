import serial, time

COM = "COM3"      # your port
BAUDS = [921600]

COMMANDS = [
    b"\xff\xff\xff",
    b"\x90\x01\xff",
    b"\x90\x01\x00\x00\xff",
    b"\x90\x01\x00\x00\x00\xff",
    b"\x90\x01\x90\x01\x00\x00\x00\xff",
    b"\x90\x90\x01\x01\x00\x00\xff",
    b"\xA5\x5A\x01\x00\xFE",
    b"\x02\x00\x00\x03",
    b"\xA5\x01\x01\x5A",
    b"\x08\x83\xff",
    b"\x08\x83\x88\xff",
]

def test_combo(baud, cmd):
    print(f"\nTrying baud={baud}, cmd={cmd}")
    try:
        ser = serial.Serial(COM, baud, timeout=0.2)
        time.sleep(0.1)

        # send command
        ser.write(cmd)
        time.sleep(0.2)

        # read data
        data = ser.read(200)
        print("Bytes received:", len(data), data[:10])
        ser.close()
    except Exception as e:
        print("Error:", e)

#for baud in BAUDS:
#    for cmd in COMMANDS:
#        test_combo(baud, cmd)

test_combo(921600,  b"\x08")
test_combo(921600,  b"\x83\x88")