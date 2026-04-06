import sys
import time
import numpy as np

from pylsl import StreamInlet, resolve_stream

# Proper Qt imports (fixes your error)
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

# -----------------------------------------
# CONFIG
# -----------------------------------------

STREAM_NAME = "KT88_1016"
CHANNEL_COUNT = 16
BUFFER_SIZE = 2000


# -----------------------------------------
# CONNECT TO LSL STREAM
# -----------------------------------------

print("Looking for LSL stream:", STREAM_NAME)
streams = resolve_stream('name', STREAM_NAME)
inlet = StreamInlet(streams[0])
print("Connected to stream.")


# -----------------------------------------
# QT APPLICATION + WINDOW
# -----------------------------------------

app = QtWidgets.QApplication([])

win = pg.GraphicsLayoutWidget(show=True, title="KT88-1016 EEG Viewer")
win.resize(1200, 800)
win.setWindowTitle("KT88 EEG Real-Time Viewer")

plots = []
curves = []

# rolling buffer
data_buffers = np.zeros((CHANNEL_COUNT, BUFFER_SIZE))

for ch in range(CHANNEL_COUNT):
    p = win.addPlot(row=ch, col=0)
    p.setLabel('left', f"Ch {ch+1}")
    p.setYRange(-400, 400)
    curve = p.plot()
    plots.append(p)
    curves.append(curve)


# -----------------------------------------
# UPDATE LOOP
# -----------------------------------------

def update():
    global data_buffers

    sample, ts = inlet.pull_sample(timeout=0.0)
    #print(sample)
    if sample is None:
        return

    sample = np.array(sample)

    # shift left and append new sample
    data_buffers = np.roll(data_buffers, -1, axis=1)
    data_buffers[:, -1] = sample

    # update all curves
    for ch in range(CHANNEL_COUNT):
        curves[ch].setData(data_buffers[ch])


timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(5)


# -----------------------------------------
# START APP
# -----------------------------------------

QtWidgets.QApplication.instance().exec_()