import joblib
import os

models_dir = '../models'

if not os.path.exists(models_dir):
    print(f"Directory '{models_dir}' does not exist.")
    exit()

files = [f for f in os.listdir(models_dir) if f.endswith('.joblib')]
if not files:
    print("No .joblib files found in 'models/' directory.")
    exit()

print("Available models:")
for i, file in enumerate(files):
    print(f"{i}: {file}")

try:
    choice = input("Enter the number of the model to load: ")
    choice = int(choice)
    if choice < 0 or choice >= len(files):
        print("Invalid choice.")
        exit()
    model_file = os.path.join(models_dir, files[choice])
except ValueError:
    print("Invalid input.")
    exit()

try:
    model = joblib.load(model_file)
    print(f"Model {model_file} loaded successfully.")
    print(f"Type: {type(model)}")
    print(f"Model representation:\n{model}")
    
    # If it's a scikit-learn model, show details
    if hasattr(model, 'get_params'):
        print("\nModel Parameters:")
        print(model.get_params())
    
    if hasattr(model, 'coef_'):
        print(f"\nCoefficients shape: {model.coef_.shape}")
        print(f"Coefficients: {model.coef_}")
        
except Exception as e:
    print(f"Error loading model: {e}")
