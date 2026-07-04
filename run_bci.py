import time
import joblib
import os
from datetime import datetime
from pybci_lib.pybci import PyBCI
import pylsl
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

# Model configuration
MODELS = {
    "svm": SVC(kernel='linear'),
    "rf": RandomForestClassifier(n_estimators=100)
}
SELECTED_MODEL = "svm" # Switch this to "rf" to use Random Forest

def save_model(model, scaler, models_dir="models"):
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"model_{timestamp}.joblib"
    filepath = os.path.join(models_dir, filename)
    joblib.dump({"model": model, "scaler": scaler}, filepath)
    print(f"Model saved to '{filepath}'")

def get_model_path():
    models_dir = 'models'
    if not os.path.exists(models_dir):
        return None
    
    files = [f for f in os.listdir(models_dir) if f.endswith('.joblib')]
    if not files:
        return None

    print("\nAvailable models:")
    for i, file in enumerate(files):
        print(f"{i}: {file}")
    
    try:
        choice = input("Enter the number of the model to load, or press Enter to train new: ")
        if choice.strip() == "":
            return None
        choice = int(choice)
        if 0 <= choice < len(files):
            return os.path.join(models_dir, files[choice])
        else:
            print("Invalid choice, training new model.")
            return None
    except ValueError:
        print("Invalid input, training new model.")
        return None

if __name__ == '__main__':
    # Initialize PyBCI
    # It will automatically try to find available streams
    # You might need to specify stream names if auto-discovery fails
    load_model_path = get_model_path()
    
    if load_model_path and os.path.exists(load_model_path):
        print(f"Loading model from {load_model_path}")
        loaded_data = joblib.load(load_model_path)
        if isinstance(loaded_data, dict):
            clf = loaded_data["model"]
            scaler = loaded_data.get("scaler", None)
        else:
            clf = loaded_data
            scaler = None
            print("Warning: Old model format detected, no scaler found. Inference may fail if a scaler was used during training.")
        bci = PyBCI(createPseudoDevice=False, markerStream=["Markers_Contec"], clf=clf, scaler=scaler)
        is_training = False
    else:
        print("Training new model.")
        bci = PyBCI(createPseudoDevice=False, markerStream=["Markers_Contec"], 
                    clf=MODELS[SELECTED_MODEL]) 
        is_training = True
    
    # Wait for connections
    print("Connecting to LSL streams...")
    while not bci.connected:
        bci.Connect()
        time.sleep(1)
    
    if is_training:
        print("Connected. Starting training...")
        bci.TrainMode()
    else:
        print("Connected. Starting inference...")
        bci.TestMode()
    
    try:
        if is_training:
            while True:
                # Check marker count
                currentMarkers = bci.ReceivedMarkerCount()
                print(f"Markers received: {currentMarkers}", end="\r")
                
                # If enough markers, switch to test mode
                if len(currentMarkers) > 1:
                    min_epochs = min([val[1] for val in currentMarkers.values()])
                    if min_epochs >= bci.minimumEpochsRequired:
                        print("\nEnough markers. Training...")
                        # Wait until the model is trained
                        while True:
                            classInfo = bci.CurrentClassifierInfo()
                            # If 'model' is None, check 'clf' (sklearn)
                            model = classInfo["model"] if classInfo["model"] is not None else classInfo["clf"]
                            scaler = classInfo["scaler"]
                            if model is not None:
                                print("Model trained.")
                                bci.TestMode()
                                save_model(model, scaler)
                                break
                            time.sleep(1)
                        break
                time.sleep(0.5)
        
        while True:
            markerGuess = bci.CurrentClassifierMarkerGuess()
            if markerGuess:
                print(f"\n[BCI LOG] Pattern recognized: {markerGuess}")
            else:
                print(f"Current marker estimation: {markerGuess}", end="\r")
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        print("\nStopping.")
        bci.StopThreads()
