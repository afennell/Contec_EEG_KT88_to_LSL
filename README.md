1 

# Contec KT88-1600-2400-3200 to LSL
Script used to decode serial data stream of Contec **KT88-1600-2400** EEG amplifiers and to stream it to the local network via LSL

**Updates**
15/07/2022 On request of some users a new script for **KT88-3200** to LSL has been created
02/12/2021 On request of some users a new script for **KT88-1600** to LSL has been created

Contec KT88-1600
https://contecmed.eu/products/kt88-digital-brain-electric-activity-mapping

Contec KT88-2400 
https://contecmed.eu/products/kt88-2400-digital-eeg-and-mapping-system

Contec KT88-3200 
https://contecmed.eu/products/kt88-3200-digital-32-channel-eeg-machine-mapping-system-2-tripods-brain-electric-contec

**Requirements**<br />
<br />
Python 3.(9)<br />
pylsl<br />
pyserial<br />
<br />
to install depdendencies `run pip3 install pylsl pyserial`<br />
<br />
Once downloaded KT88-1600_LSL_streaming.py or KT88-2400_LSL_streaming.py set the desired port an run the script with <br />
`python3 KT88-2400_LSL_streaming.py COM_PORT` the script
<br /><br />

The ready binaries for Windows x64 are available https://github.com/miladinovic/Contec_KT88-2400_LSL/releases

For Windows it is not necassery to install addional libraries, just make sure that you have changed the port to COM20, then run the EEG24 program to verify if the device still works.

To change port go to Control Panel -> Device Manager -> Ports (COM&LPT) -> Right-click to the com to the UART to USB bridge and select "Properties" -> Port settings tab -> button Advance and change to port COM20 click OK and then run te EEG24.

Choose the desired settings HW filter 0.3-35Hz ON or OFF, as well as for KT88-2400 only, a reference electrode (AA=A1+A2, AV=Average, BN=Balanced-non cephalic) .

For KT88-1600 16 channels with state of 100Hz will be streamed to the local network via LSL protocol with the following order ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2', 'F7', 'F8', 'T3', 'T4', 'T5', 'T6','ECG1','ECG2']

For KT88-2400 26 channels with state of 200Hz will be streamed to the local network via LSL protocol with the following order ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2', 'F7', 'F8', 'T3', 'T4', 'T5', 'T6', 'Fz', 'Pz', 'Cz', 'Pg1', 'Pg2', 'EOGR', 'EOGL', 'EMG', 'BR', 'ECG']


For KT88-3200 32 channels with state of 200Hz will be streamed to the local network via LSL protocol with the following order ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2', 'F7', 'F8', 'T7', 'T8','P7', 'P8',  'Fz', 'Pz', 'Cz', 'PG1', 'PG2','AFz', 'FCz', 'CPz',  'CP3', 'CP4','FC3', 'FC4', 'TP7', 'TP8', 'FT7', 'FT8']


**Communication protocol and commands**<br />
<br />
**Acquisition and filter control (commands in hex format)**<br />
90 01 Start Acquisition<br />
90 02 Stop acquisition<br />
90 03 Enable HW filter 0.5-35Hz<br />
90 04 Disable HW filter<br />
90 05 Start impedance measurement (KT88-2400/3200 only)<br />
90 06 Disable impedance measurement (KT88-2400/3200 only)<br />
<br />
**Setting physical reference electrode (KT88-2400/3200 only)**<br />

91 01 AA reference (left hemisphere referenced to the left ear lobe, right to the right earlobe)<br />
91 02 A1 reference (all electrodes referenced to the A1)<br />
91 03 A2 reference<br />
91 04 AVG (average reference)<br />
91 05 Cz reference<br />
91 06 BN (balanced noncephalic reference)<br />
<br />
**Montage setup (KT88-2400/3200 only)**<br />

92 0X (9 defined montages X=1,...,9, the montage can be explored by going to System configuration -> montage ways, see screenshots bellow). Changes of default montage always follow the command 91 04 (avg reference).<br />
<br /><br />

**Uknown commands**<br />
80 00<br />
81 00<br />
<br />
Example of the default KT88-2400 system settings sequence sent by the provided EEG software.<br />
<br />
*90 02 //stop acquisition<br />
80 00 //?<br />
81 00 //?<br />
91 06 //set BN reference<br />
90 09 //?<br />
90 03 //Enable HW filter<br />
90 06 //Disable impedance reading<br />
90 01 //Start data acquisition<br />
... DATA STREAM ...<br />
90 02 //Stop acquisition*<br />
<br />
**Data**<br />
Baud rate 921600<br />
Data sampling rate 100Hz or 200Hz<br />
Encoding bits 12<br />
Number of channels 18 or 26<br />

Protocol: https://github.com/miladinovic/Contec_KT88-2400_LSL/blob/main/serial_decoding_protocol.txt

**Disclamer**
The provided software is made for educational and research purposes only. It is not by any means a substitute for provided software by manufacturer.

**Support my work**
If you find this script useful for your experiments, please cite my works. Thank you!

`Miladinović, Aleksandar, et al. "Effect of power feature covariance shift on BCI spatial-filtering techniques: A comparative study." Computer Methods and Programs in Biomedicine 198 (2021): 105808.`

`Miladinović, Aleksandar, et al. "Performance of EEG Motor-Imagery based spatial filtering methods: A BCI study on Stroke patients." Procedia Computer Science 176 (2020): 2840-2848.`

`Miladinović, Aleksandar, et al. "Evaluation of Motor Imagery-Based BCI methods in neurorehabilitation of Parkinson’s Disease patients." 2020 42nd Annual International Conference of the IEEE Engineering in Medicine & Biology Society (EMBC). IEEE, 2020.`

**Montage modes**<br />
92 01<br />
![alt text](1.PNG))<br />
92 02<br />
![alt text](2.PNG))<br />
92 03<br />
![alt text](3.PNG))<br />
92 04<br />
![alt text](4.PNG))<br />
92 05<br />
![alt text](5.PNG))<br />
92 06<br />
![alt text](6.PNG))<br />
92 07<br />
![alt text](7.PNG))<br />
92 08<br />
![alt text](8.PNG))<br />
92 09<br />
![alt text](9.PNG))<br />

#### KT88 16 Channels
- This version requires a specific set of codes in order to make the acquisition start
- \x08 \x83 \x88 (Adriana Fennell)

#### EEG Viewer
- Run the LSL Stream Viewer to visualize the KT88 output
  ```bash
  python lsl_eeg_viewer.py
  ```

#### PyBCI Integration
- **Ensure Dependencies:** You must install the following Python packages in your environment:
   ```bash
   pip install scikit-learn torch tensorflow antropy scipy numpy pylsl
   ```
- **`run_bci.py`:** Created a new script to orchestrate the BCI pipeline, connecting to your existing EEG LSL stream and enabling the training/testing logic.
- **`send_markers.py`:** Added a utility script to create an LSL marker stream (`"Markers"`), which is required by `PyBCI` for epoching the data during training.

#### How to Use
1. **Start the EEG Stream:** Run your existing `kt88_1016_lsl.py` script.
   
2. **Run BCI Pipeline:** Start the BCI processing in a new terminal:
   ```bash
   python run_bci.py
   ```
   
3. **Send Training Markers:** Start the marker sender in another terminal:
   ```bash
   python send_markers.py
   ```
   Follow the prompts to send markers like `baseline` and `arm_move`. Once the minimum number of epochs (default is 10 of each) is reached, `run_bci.py` will automatically switch to Test Mode and provide estimations.

#### Notes
- **LSL Stream:** `PyBCI` automatically searches for available EEG and Marker streams. If `run_bci.py` fails to connect, ensure the name of your EEG stream matches what `PyBCI` expects, or explicitly pass the stream name in `PyBCI(...)`.
- **Classifier Configuration:** By default, it uses a support vector machine (SVM) from `scikit-learn`. You can customize the classifier by passing a different `clf`, `model`, or `torchModel` to the `PyBCI` constructor in `run_bci.py`.

### Recommended Execution Sequence

To run the BCI pipeline correctly, start the scripts in this specific order to ensure data streams are available before `PyBCI` attempts to connect:

1.  **Start the EEG Stream (`kt88_1016_lsl.py`)**
    This script initializes the connection to your EEG hardware and streams data via LSL.
    ```bash
    python kt88_1016_lsl.py
    ```

2.  **Start the Marker Stream (`send_markers.py`)**
    `PyBCI` requires a marker stream to epoch the data.
    ```bash
    python send_markers.py
    ```
    *Keep this terminal open, as you will need to input markers (e.g., `baseline`, `arm_move`) here to train the model.*

3.  **Run the BCI Pipeline (`run_bci.py`)**
    Once the EEG and Marker streams are active, start the BCI processing.
    ```bash
    python run_bci.py
    ```

### Troubleshooting
*   **Order Matters:** If `run_bci.py` is started first, it may not find the streams.
*   **Verification:** If you are unsure if streams are active, run `test_lsl.py` to confirm that both `KT88_1016` and `Markers` streams are discoverable.
*   **Dependencies:** Ensure required packages are installed:

#### How to proceed with training:
1.  **Go to the terminal where `send_markers.py` is running.**
2.  **Start sending markers** to label your brain signals.
    *   **For `baseline`:** Send "baseline" when you are sitting still and not moving your arm.
    *   **For `arm_move`:** Send "arm_move" while you are performing the specific arm movement you want to recognize.
3.  **Continue sending markers:**
    *   `PyBCI` is configured by default to require at least **10 examples of each marker** (10 "baseline" and 10 "arm_move") to begin training the classifier.
    *   As you send these markers, look at the output in the `run_bci.py` terminal; it will likely show the count of received markers.

#### What happens next:
Once `run_bci.py` detects that it has gathered enough training epochs (the required number for each marker type), it will:
1.  Automatically begin fitting the classification model.
2.  Switch to **Test Mode** on its own.
3.  Once in Test Mode, it will start printing the predicted markers to your `run_bci.py` terminal as it analyzes your real-time EEG data.
