"""
Created on Jul 14, 2022

@author: Aleksandar Miladinovic email: alex.miladinovich@gmail.com

Python script used to decode serial data stream of Contec KT88-3200 EEG amplifier and stream it to the local network via LSL

"""
import time
import serial
from pylsl import StreamInfo, StreamOutlet
import sys
import serial.tools.list_ports

ser = serial.Serial()
if len(sys.argv) > 1:
    COM_PORT = sys.argv[1]
else:
    # Port not given, using default
    if sys.platform == 'win32':
        COM_PORT = 'COM20'
    else:
        COM_PORT = '/dev/cu.usbserial-140'

ser = serial.Serial(
    port=COM_PORT,
    baudrate=921600, parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS, xonxoff=False, rtscts=False, dsrdtr=False
)

def adc_to_eeg_voltage(adc_value, vref=2.5):
    """
    Convert a 12-bit ADC value (0-4095) from MSP430F247 EEG system to voltage.

    :param adc_value: Integer (0-4095) from ADC
    :param vref: Reference voltage (default 3.3V)
    :return: EEG voltage in Volts
    """
    return ((adc_value / 4095) - 0.5) * vref



def send_default_configuration_to_EEG():
    # Stop acquisition
    packet = bytearray()
    packet.append(0xff)
    ser.write(packet)
    time.sleep(0.3)

    # Send new default configuration
    packet = bytearray()
    packet.append(0x08)
    packet.append(0x83)
    packet.append(0x42)
    packet.append(0x88)
    ser.write(packet)
    time.sleep(0.3)


def find_packet_start():
    """ Reads the stream until 'FF FF' is found, ensuring packet alignment """
    while True:
        sync_bytes = ser.read_until(expected=b"\xFF\xFF")
        if sync_bytes.endswith(b"\xFF\xFF"):
            return  # Found packet start


def main():
    print("Send default")
    send_default_configuration_to_EEG()

    print("Setup LSL")
    stream_info_KT88 = StreamInfo('KT88', 'EEG', 32, 200, 'float32', 'kt_88_3200_EEG')

    # Add channel labels
    channels = stream_info_KT88.desc().append_child("channels")
    ch_labels = [
        "Fp1", "Fp2", "F3", "F4", "C3", "C4", "P3", "P4", "O1", "O2",
        "F7", "F8", "T7", "T8", "P7", "P8", "Fz", "Pz", "Cz", "PG1", "PG2",
        "AFz", "FCz", "CPz", "CP3", "CP4", "FC3", "FC4", "TP7", "TP8", "FT7", "FT8"
    ]

    for c in ch_labels:
        ch = channels.append_child("channel")
        ch.append_child_value("label", c)

    # Create an LSL outlet
    kt88_outlet = StreamOutlet(stream_info_KT88)

    ser.flushInput()
    ser.flushOutput()

    while True:
        # Find the start of a valid packet
        find_packet_start()

        # Read next 64 bytes (32 EEG channels, 2 bytes each)
        eeg_data = ser.read(64)

        if len(eeg_data) != 64:
            continue  # Skip if we didn't get the full packet

        channel_values = []
        for i in range(32):
            low_byte = eeg_data[i * 2]
            high_byte = eeg_data[i * 2 + 1]

            # Extract 12-bit value
            value = ((high_byte << 4) | (low_byte & 0x0F))

            # Convert to signed 12-bit value (-2048 to 2047)
            value = adc_to_eeg_voltage(value)

            # Store as float
            channel_values.append(float(value))

        if kt88_outlet.have_consumers():
            kt88_outlet.push_sample(channel_values)


if __name__ == '__main__':
    main()