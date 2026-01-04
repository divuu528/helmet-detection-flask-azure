import os
import io
import json
import numpy as np
from flask import Flask, render_template, request
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

app = Flask(__name__)

# Filenames - must be in your root folder next to app.py
MODEL_PATH = "helmet_model.keras"
JSON_PATH = "class_indices.json"

# Load model and indices on startup
try:
    if os.path.exists(MODEL_PATH) and os.path.exists(JSON_PATH):
        model = load_model(MODEL_PATH)
        with open(JSON_PATH, "r") as f:
            class_indices = json.load(f)
        
        # Map indices to technical names from your JSON
        CLASS_NAMES = {int(v): k for k, v in class_indices.items()}
        print("SUCCESS: Model and class indices loaded.")
    else:
        print("ERROR: Model or JSON file not found.")
        model = None
except Exception as e:
    print(f"Startup Error: {e}")
    model = None

# Mapping for your index.html display
FRIENDLY_NAMES = {
    "person_helmet": "Person with Helmet",
    "person_no_helmet": "Person without Helmet",
    "background": "No Person Detected"
}

@app.route('/', methods=['GET', 'POST'])
def index():
    prediction = None
    confidence = None
    
    if request.method == 'POST':
        if model is None:
            return render_template('index.html', prediction="MODEL ERROR: CHECK LOGS", confidence=0)
            
        file = request.files.get('image')
        if not file:
            return render_template('index.html', prediction="No image uploaded", confidence=0)

        try:
            # Preprocessing
            img_bytes = io.BytesIO(file.read())
            img = image.load_img(img_bytes, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0) / 255.0

            # Prediction
            preds = model.predict(img_array)[0]
            idx = int(np.argmax(preds))
            
            tech_name = CLASS_NAMES.get(idx, "background")
            prediction = FRIENDLY_NAMES.get(tech_name, tech_name)
            confidence = round(float(preds[idx]) * 100, 2)
            
        except Exception as e:
            print(f"Prediction Error: {e}")
            prediction = "Error processing image"

    return render_template('index.html', prediction=prediction, confidence=confidence)

if __name__ == "__main__":
    # Uses Azure's port or defaults to 8000 for local testing
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)