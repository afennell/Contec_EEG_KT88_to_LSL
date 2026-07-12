"""
Created on Sep 10, 2025

@author: Aleksandar Miladinovic

Python script used to decode serial data stream of Contec KT88-1600/1800 amplifier
but using updated KT88-3200-style decoding (2 bytes per channel).
Streams via LSL with 18 channels at 100 Hz.
"""

import time
import serial
from pylsl import StreamInfo, StreamOutlet
import sys
import serial.tools.list_ports

if len(sys.argv) > 1:
    COM_PORT=sys.argv[1]
else:
    # port not given, using default
    if sys.platform == 'win32':
        COM_PORT='COM20'
    else:
        COM_PORT='/dev/cu.usbserial-1420'

ser = serial.Serial(port=COM_PORT,
                    baudrate=921600, parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,xonxoff=False,rtscts=False,dsrdtr=False)

def start_acquisition():
    #packet = bytearray([0x90, 0x01])
    packet = bytearray([0x08, 0x83, 0x88])
    return ser.write(packet)

def stop_acquisition():
    #packet = bytearray([0x90, 0x02])
    packet = bytearray([0xFF])
    return ser.write(packet)

def send_default_configuration_to_EEG():
    # stop acquisition
    ser.write(bytearray([0x90, 0x02])); time.sleep(0.3)
    ser.write(bytearray([0x80, 0x00])); time.sleep(0.3)
    ser.write(bytearray([0x81, 0x00])); time.sleep(0.3)
    ser.write(bytearray([0x91, 0x01])); time.sleep(0.3)
    ser.write(bytearray([0x90, 0x03])); time.sleep(0.3)
    ser.write(bytearray([0x90, 0x06])); time.sleep(0.3)

    ser.flushInput()
    ser.flushOutput()
    return 1

def adc_to_eeg_voltage(raw_value):
    """Convert 12-bit value to signed and scale"""
    if raw_value & 0x800:
        raw_value -= 0x1000
    # Scale to uV (assuming factor 10)
    return float(raw_value)

def main():
    print("Send default")
    send_default_configuration_to_EEG();

    print("Start acquisition")
    start_acquisition()

    print("Setup LSL")
    stream_info_KT88 = StreamInfo('KT88', 'EEG', 16, 100, 'float32', 'kt_88_1600_EEG')

    # add channel labels
    channels = stream_info_KT88.desc().append_child("channels")
    ch_labels = ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2',
                 'F7', 'F8', 'T3', 'T4', 'T5', 'T6']
    for c in ch_labels:
        ch = channels.append_child("channel")
        ch.append_child_value("label", c)

    kt88_outlet = StreamOutlet(stream_info_KT88)
    print("Streaming...")

    ser.flushInput()
    ser.flushOutput()

    # init channels
    channel = [0] * 16

    try:
        while 1:
            # find marker (sync byte)
            ser.read_until(expected=b"\xA0")

            # read 32 bytes (16 channels × 2 bytes)
            eeg_data = ser.read(32)
            if len(eeg_data) != 32:
                continue

            for i in range(16):
                low = eeg_data[i*2]
                high = eeg_data[i*2+1]
                raw_value = ((high << 4) | (low & 0x0F))
                channel[i] = adc_to_eeg_voltage(raw_value)

            if kt88_outlet.have_consumers():
                kt88_outlet.push_sample(channel)
    except KeyboardInterrupt:
        print("Ctrl+C pressed, sending command...")
        ser.write(b'\xFF')  # send your command
        ser.flush()
    finally:
        ser.close()

if __name__ == '__main__':
    main()
