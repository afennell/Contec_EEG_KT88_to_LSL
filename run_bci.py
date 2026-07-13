import sys
import time
import joblib
import os
from datetime import datetime
from pybci_lib.pybci import PyBCI
import pylsl
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

# Try importing optional deep learning libraries
try:
    from tensorflow import keras
    from tensorflow.keras import layers
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False

try:
    import torch
    import torch.nn as nn
    HAS_PYTORCH = True
except ImportError:
    HAS_PYTORCH = False

# Model configuration
MODELS = {
    "svm": SVC(kernel='linear'),
    "rf": RandomForestClassifier(n_estimators=100),
    "lr": LogisticRegression(max_iter=1000),
    "knn": KNeighborsClassifier(n_neighbors=5),
    "dt": DecisionTreeClassifier(random_state=42)
}

# Deep learning model creators
def create_tensorflow_model(input_dim=None):
    """Create a simple Keras neural network"""
    model = keras.Sequential([
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(32, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(2, activation='softmax')  # Adjust output layer as needed
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

def create_pytorch_model(input_dim=None):
    """Create a simple PyTorch neural network with training function"""
    class SimpleNet(nn.Module):
        def __init__(self, input_dim=32):
            super(SimpleNet, self).__init__()
            self.fc1 = nn.Linear(input_dim, 64)
            self.fc2 = nn.Linear(64, 32)
            self.fc3 = nn.Linear(32, 2)
            self.relu = nn.ReLU()
            self.dropout = nn.Dropout(0.2)
        
        def forward(self, x):
            # Flatten if needed
            if len(x.shape) > 2:
                x = x.reshape(x.shape[0], -1)
            x = self.relu(self.fc1(x))
            x = self.dropout(x)
            x = self.relu(self.fc2(x))
            x = self.dropout(x)
            x = self.fc3(x)
            return x
    
    model = SimpleNet(input_dim if input_dim else 32)
    
    def train_and_evaluate(x_train, x_test, y_train, y_test):
        """Train the model and return accuracy and trained model"""
        import sys
        # Flatten data if 3D
        if len(x_train.shape) == 3:
            x_train = x_train.reshape(x_train.shape[0], -1)
            x_test = x_test.reshape(x_test.shape[0], -1)
        
        x_train = torch.FloatTensor(x_train)
        x_test = torch.FloatTensor(x_test)
        y_train = torch.LongTensor(y_train)
        y_test = torch.LongTensor(y_test)
        
        print(f"[PyTorch] Training with shapes: x_train={x_train.shape}, y_train={y_train.shape}", flush=True)
        sys.stdout.flush()
        
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
        # Training loop
        model.train()
        epochs = 50
        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = model(x_train)
            loss = criterion(outputs, y_train)
            loss.backward()
            optimizer.step()
            if (epoch + 1) % 10 == 0:
                print(f"[PyTorch] Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}", flush=True)
                sys.stdout.flush()
        
        print(f"[PyTorch] Training complete, evaluating...", flush=True)
        sys.stdout.flush()
        
        # Evaluate
        model.eval()
        with torch.no_grad():
            test_outputs = model(x_test)
            _, predictions = torch.max(test_outputs, 1)
            accuracy = (predictions == y_test).float().mean().item()
            print(f"[PyTorch] Accuracy: {accuracy:.4f}", flush=True)
        
        model.train()  # Put back in training mode
        print(f"[PyTorch] Returning: accuracy={accuracy}, model={type(model)}", flush=True)
        sys.stdout.flush()
        return accuracy, model
    
    # Store the training function as an attribute
    model.train_func = train_and_evaluate
    return model

SELECTED_MODEL = "svm" # Switch this to desired model

def save_model(model, scaler, marker_labels=None, models_dir="models"):
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"\n{'='*60}")
    print(f"[SAVING MODEL] Type: {type(model).__name__}")
    print(f"{'='*60}")
    sys.stdout.flush()
    
    try:
        # Check if it's a Keras model
        if HAS_TENSORFLOW and hasattr(model, 'save'):
            print(f"[SAVING] Detected Keras/TensorFlow model")
            sys.stdout.flush()
            filename = f"model_keras_{timestamp}.keras"
            filepath = os.path.join(models_dir, filename)
            print(f"[SAVING] Writing model to: {filepath}")
            sys.stdout.flush()
            model.save(filepath)
            print(f"[SAVING] ✓ Model saved successfully!")
            sys.stdout.flush()
            # Also save scaler separately
            if scaler:
                scaler_filepath = os.path.join(models_dir, f"scaler_keras_{timestamp}.joblib")
                print(f"[SAVING] Writing scaler to: {scaler_filepath}")
                sys.stdout.flush()
                joblib.dump(scaler, scaler_filepath)
                print(f"[SAVING] ✓ Scaler saved!")
                sys.stdout.flush()
            print(f"[SAVING] ✓✓✓ Keras model saved to: {filepath}")
            print(f"{'='*60}\n")
            sys.stdout.flush()
            return
        
        # Check if it's a PyTorch model
        if HAS_PYTORCH and isinstance(model, nn.Module):
            print(f"[SAVING] Detected PyTorch model")
            sys.stdout.flush()
            # Remove the training function before saving
            if hasattr(model, 'train_func'):
                delattr(model, 'train_func')
            filename = f"model_pytorch_{timestamp}.pt"
            filepath = os.path.join(models_dir, filename)
            print(f"[SAVING] Writing weights to: {filepath}")
            sys.stdout.flush()
            torch.save(model.state_dict(), filepath)
            print(f"[SAVING] ✓ Weights saved successfully!")
            sys.stdout.flush()
            
            if scaler:
                scaler_filepath = os.path.join(models_dir, f"scaler_pytorch_{timestamp}.joblib")
                print(f"[SAVING] Writing scaler to: {scaler_filepath}")
                sys.stdout.flush()
                joblib.dump(scaler, scaler_filepath)
                print(f"[SAVING] ✓ Scaler saved successfully!")
                sys.stdout.flush()
            
            if marker_labels:
                labels_filepath = os.path.join(models_dir, f"labels_pytorch_{timestamp}.joblib")
                print(f"[SAVING] Writing labels to: {labels_filepath}")
                sys.stdout.flush()
                joblib.dump(marker_labels, labels_filepath)
                print(f"[SAVING] ✓ Labels saved: {marker_labels}")
                sys.stdout.flush()
            
            print(f"[SAVING] ✓✓✓ PyTorch model saved to: {filepath}")
            print(f"{'='*60}\n")
            sys.stdout.flush()
            return
        
        # Otherwise save as sklearn model
        filename = f"model_{timestamp}.joblib"
        filepath = os.path.join(models_dir, filename)
        joblib.dump({"model": model, "scaler": scaler}, filepath)
        print(f"Model saved to '{filepath}'")
    except Exception as e:
        print(f"Error saving model: {e}")

def get_model_path():
    models_dir = 'models'
    if not os.path.exists(models_dir):
        return None, None
    
    # Only include actual model files, exclude scaler files
    files = [f for f in os.listdir(models_dir) if f.endswith(('.joblib', '.keras', '.h5', '.pt')) and 'scaler' not in f]
    if not files:
        return None, None

    print("\nAvailable models:")
    for i, file in enumerate(files):
        print(f"{i}: {file}")
    
    try:
        choice = input("Enter the number of the model to load, or press Enter to train new: ")
        if choice.strip() == "":
            return None, None
        choice = int(choice)
        if 0 <= choice < len(files):
            return os.path.join(models_dir, files[choice]), files[choice]
        else:
            print("Invalid choice, training new model.")
            return None, None
    except ValueError:
        print("Invalid input, training new model.")
        return None, None

def startup_menu():
    """Interactive startup menu for mode and model selection"""
    print("\n" + "="*50)
    print("      BCI System - Startup Configuration")
    print("="*50)
    
    # Default to training PyTorch if in non-interactive mode
    try:
        # Ask for mode
        while True:
            print("\nSelect mode:")
            print("1. Train a new model")
            print("2. Load an existing model for inference")
            mode_choice = input("Enter choice (1 or 2): ").strip()
            
            if mode_choice == "1":
                # Ask for model type
                while True:
                    print("\nSelect model type:")
                    print("--- Scikit-Learn Models ---")
                    print("1. SVM (Support Vector Machine) - Linear kernel")
                    print("2. Random Forest - 100 estimators")
                    print("3. Logistic Regression")
                    print("4. KNN (K-Nearest Neighbors)")
                    print("5. Decision Tree")
                    
                    if HAS_TENSORFLOW:
                        print("--- TensorFlow/Keras Models ---")
                        print("6. Keras Neural Network")
                    
                    if HAS_PYTORCH:
                        print("--- PyTorch Models ---")
                        print("7. PyTorch Neural Network")
                    
                    model_choice = input("Enter choice: ").strip()
                    
                    model_map = {
                        "1": ("svm", "sklearn"),
                        "2": ("rf", "sklearn"),
                        "3": ("lr", "sklearn"),
                        "4": ("knn", "sklearn"),
                        "5": ("dt", "sklearn"),
                    }
                    
                    if HAS_TENSORFLOW:
                        model_map["6"] = ("keras", "tensorflow")
                    
                    if HAS_PYTORCH:
                        model_map["7"] = ("pytorch", "pytorch")
                    
                    if model_choice in model_map:
                        model_name, model_lib = model_map[model_choice]
                        return None, model_name, model_lib
                    else:
                        print("Invalid choice. Please enter a valid option.")
                
            elif mode_choice == "2":
                model_path, model_filename = get_model_path()
                if model_path:
                    return model_path, None, None
                else:
                    print("No models found. Please train a new model first.")
                    continue
            else:
                print("Invalid choice. Please enter 1 or 2.")
    except EOFError:
        # Non-interactive mode - default to PyTorch training
        print("[INFO] Non-interactive mode detected. Defaulting to PyTorch training.")
        return None, "pytorch", "pytorch"

if __name__ == '__main__':
    # Interactive startup menu
    load_model_path, model_name, model_lib = startup_menu()
    
    if load_model_path and os.path.exists(load_model_path):
        print(f"\nLoading model from {load_model_path}")
        
        if load_model_path.endswith(('.h5', '.keras')):
            # Load Keras model
            model = keras.models.load_model(load_model_path)
            clf = None
            torchModel = None
            # Try to load scaler - handle both .h5 and .keras extensions
            if load_model_path.endswith('.keras'):
                scaler_path = load_model_path.replace('.keras', '.joblib')
            else:
                scaler_path = load_model_path.replace('.h5', '.joblib')
            
            if os.path.exists(scaler_path):
                scaler = joblib.load(scaler_path)
                print(f"Scaler loaded from {scaler_path}")
            else:
                scaler = None
                print("Warning: Scaler file not found. Inference may have scaling issues.")
            
        elif load_model_path.endswith('.pt'):
            # Load PyTorch model
            torchModel = create_pytorch_model()
            torchModel.load_state_dict(torch.load(load_model_path))
            clf = None
            model = None
            # Try to load scaler
            scaler_path = load_model_path.replace('.pt', '.joblib')
            scaler = joblib.load(scaler_path) if os.path.exists(scaler_path) else None
            
        else:
            # Load sklearn model
            loaded_data = joblib.load(load_model_path)
            if isinstance(loaded_data, dict):
                clf = loaded_data.get("model")
                scaler = loaded_data.get("scaler", None)
                model = loaded_data.get("tensorflow_model")
                torchModel = loaded_data.get("pytorch_model")
            else:
                clf = loaded_data
                scaler = None
                model = None
                torchModel = None
                print("Warning: Old model format detected, no scaler found. Inference may fail if a scaler was used during training.")
        
        # Validate sklearn model
        if clf is not None and hasattr(clf, 'estimators_') and len(clf.estimators_) == 0:
            print(f"ERROR: Model is corrupted (no estimators found). Please train a new model.")
            exit(1)
        
        bci = PyBCI(createPseudoDevice=False, markerStream=["Markers_Contec"], clf=clf, model=model, torchModel=torchModel, scaler=scaler)
        is_training = False
    else:
        print(f"\nTraining new model using {model_name.upper()} ({model_lib}).")
        
        if model_lib == "sklearn":
            clf = MODELS[model_name]
            model = None
            torchModel = None
        elif model_lib == "tensorflow":
            clf = None
            model = create_tensorflow_model()
            torchModel = None
        elif model_lib == "pytorch":
            clf = None
            model = None
            torchModel = create_pytorch_model()
        
        bci = PyBCI(createPseudoDevice=False, markerStream=["Markers_Contec"], clf=clf, model=model, torchModel=torchModel)
        is_training = True
    
    # Wait for connections
    print("Connecting to LSL streams...")
    while not bci.connected:
        bci.Connect()
        time.sleep(1)
    
        if is_training:
            print("Connected. Starting training...")
            bci.TrainMode()
            # Capture marker labels during training
            marker_labels = None
        else:
            print("Connected. Starting inference...")
            bci.TestMode()
            # Load marker labels if available
            marker_labels = None
            if load_model_path:
                models_dir = 'models'
                print(f"\nDebug: Attempting to load labels for model: {load_model_path}")
                
                # Extract timestamp from model filename
                if 'model_keras_' in load_model_path:
                    timestamp = load_model_path.split('model_keras_')[1].replace('.keras', '')
                    labels_path = os.path.join(models_dir, f"labels_keras_{timestamp}.joblib")
                    print(f"Debug: Looking for Keras labels at: {labels_path}")
                elif 'model_pytorch_' in load_model_path:
                    timestamp = load_model_path.split('model_pytorch_')[1].replace('.pt', '')
                    labels_path = os.path.join(models_dir, f"labels_pytorch_{timestamp}.joblib")
                    print(f"Debug: Looking for PyTorch labels at: {labels_path}")
                elif 'model_' in load_model_path:
                    timestamp = load_model_path.split('model_')[1].replace('.joblib', '')
                    labels_path = os.path.join(models_dir, f"model_{timestamp}.joblib")
                    print(f"Debug: Looking for sklearn labels in: {labels_path}")
                    # For sklearn models, labels are inside the joblib file
                    loaded_data = joblib.load(load_model_path)
                    marker_labels = loaded_data.get("class_labels") if isinstance(loaded_data, dict) else None
                    if marker_labels:
                        print(f"✓ Loaded class labels from sklearn model: {marker_labels}")
                    else:
                        print("✗ No class labels found in sklearn model file")
                else:
                    labels_path = None
                    marker_labels = None
                    print("Debug: Could not determine model type")
                
                # Load labels for keras/pytorch
                if labels_path and os.path.exists(labels_path):
                    marker_labels = joblib.load(labels_path)
                    print(f"✓ Loaded class labels: {marker_labels}")
                elif labels_path and not os.path.exists(labels_path):
                    marker_labels = None
                    print(f"✗ Class labels file not found at: {labels_path}")
                    print("  Predictions will show numeric indices.")
    
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
                        training_start = time.time()
                        max_wait = 300  # 5 minutes max
                        check_count = 0
                        while True:
                            classInfo = bci.CurrentClassifierInfo()
                            # Priority: torchModel > model > clf
                            model = classInfo.get("torchModel") if classInfo.get("torchModel") is not None else None
                            if model is None:
                                model = classInfo.get("model") if classInfo.get("model") is not None else None
                            if model is None:
                                model = classInfo.get("clf") if classInfo.get("clf") is not None else None
                            scaler = classInfo.get("scaler")
                            accuracy = classInfo.get("accuracy", 0)
                            
                            elapsed = time.time() - training_start
                            check_count += 1
                            
                            # Only print every 10 checks to avoid spam
                            if check_count % 10 == 0:
                                print(f"[Training] Check #{check_count}: model={model is not None}, accuracy={accuracy:.4f}, elapsed={elapsed:.1f}s", flush=True)
                            
                            if model is not None and accuracy > 0:
                                print(f"\n[SUCCESS] Model trained with accuracy={accuracy:.4f}!", flush=True)
                                bci.TestMode()
                                # Get and save marker labels
                                marker_labels = list(currentMarkers.keys()) if currentMarkers else None
                                print(f"Marker classes: {marker_labels}")
                                save_model(model, scaler, marker_labels)
                                break
                            
                            if elapsed > max_wait:
                                print(f"\n[ERROR] Training timeout after {max_wait}s")
                                print(f"Final state: model={model is not None}, accuracy={accuracy}")
                                break
                            time.sleep(1)
                        break
                time.sleep(0.5)
        
        while True:
            markerGuess = bci.CurrentClassifierMarkerGuess()
            if markerGuess is not None:
                # Map numeric prediction to label if available
                if marker_labels and isinstance(markerGuess, int) and markerGuess < len(marker_labels):
                    label = marker_labels[markerGuess]
                    print(f"\n[BCI LOG] Pattern recognized: {label}")
                elif marker_labels and isinstance(markerGuess, (int, float)):
                    # If we have labels but index is out of range, still try to map
                    try:
                        label = marker_labels[int(markerGuess)]
                        print(f"\n[BCI LOG] Pattern recognized: {label}")
                    except (IndexError, TypeError):
                        print(f"\n[BCI LOG] Pattern recognized: {markerGuess}")
                else:
                    print(f"\n[BCI LOG] Pattern recognized: {markerGuess}")
            else:
                print(f"Current marker estimation: {markerGuess}", end="\r")
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        print("\nStopping.")
        bci.StopThreads()
