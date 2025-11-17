import os
import re
import cv2
import joblib
import numpy as np
import pandas as pd
import pytesseract
from flask import Flask, request, jsonify, render_template, send_from_directory
from PIL import Image
from pdf2image import convert_from_path

# --- App Initialization ---
app = Flask(__name__)

# --- Load Model ---
# Ensure 'best_xgboost_model.pkl' is in the same directory as app.py
try:
    model = joblib.load('best_xgboost_model.pkl')
    print("Model loaded successfully.")
except FileNotFoundError:
    print("Error: 'best_xgboost_model.pkl' not found.")
    model = None
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# --- Feature List (from your training script) ---
# NOTE: Your training script had 'Age ' with a space. We must match it.
EXPECTED_FEATURES = [
    'Age ', 'Gender', 'Height', 'Weight', 'ap_hi', 'ap_lo', 
    'Cholesterol', 'Gluc', 'Smoke', 'Alco', 'Active'
]

# --- OCR & Extraction Logic (from your copy_of_ocr12.py) ---
def preprocess_image(img_path):
    """Preprocesses image for better OCR results."""
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return gray

def extract_text_from_image(img_path):
    """Extracts text from a single image using Tesseract."""
    try:
        preprocessed_img = preprocess_image(img_path)
        # You may need to add your tesseract path if it's not in your system PATH
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        text = pytesseract.image_to_string(preprocessed_img, lang='eng')
        return text
    except Exception as e:
        print(f"Error during OCR: {e}")
        return ""

def extract_key_values(text):
    """Uses regex to find medical values in the OCR text."""
    patterns = {
        "age": r"(age|years old|yrs|yr)[^\d]*(\d{1,3})",
        "gender": r"(gender|sex)[^\w]*(male|female|m|f)",
        "height": r"(height|ht)[^\d]*(\d{2,3})", # Simplified units
        "weight": r"(weight|wt)[^\d]*(\d{2,3})", # Simplified units
        "cholesterol": r"(cholesterol|chol)[^\d]*(\d{2,3})",
        "glucose": r"(glucose|gluc)[^\d]*(\d{2,3})",
        "blood_pressure": r"(bp|blood pressure)[^\d:]*\s*[:]?\s*(\d{2,3})(?:\s*/\s*(\d{2,3}))?"
    }
    
    results = {}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if matches:
            if key == "blood_pressure":
                results['ap_hi'] = matches[0][1]
                if len(matches[0]) > 2 and matches[0][2]:
                    results['ap_lo'] = matches[0][2]
            elif key == "gender":
                gender_val = matches[0][1].lower()
                if gender_val.startswith('m'):
                    results['gender'] = 'Male'
                elif gender_val.startswith('f'):
                    results['gender'] = 'Female'
            else:
                results[key] = matches[0][1] # Get the numeric value
    
    return results

# --- Backend API Endpoints ---

@app.route('/extract', methods=['POST'])
def handle_extraction():
    """
    Handles file upload, performs OCR, and returns extracted JSON data.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save temp file
    temp_dir = 'temp_files'
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    file.save(file_path)

    full_text = ""
    try:
        if file.filename.lower().endswith('.pdf'):
            
            # ---!!! THIS IS THE FIX !!!---
            # Update this path to your Poppler 'bin' directory
            poppler_install_path = r"C:\Program Files\poppler-25.07.0\Library\bin" 
            
            pages = convert_from_path(
                file_path, 
                dpi=200,
                poppler_path=poppler_install_path
            )
            
            for i, page in enumerate(pages):
                img_page_path = os.path.join(temp_dir, f'page_{i}.jpg')
                page.save(img_page_path, 'JPEG')
                full_text += extract_text_from_image(img_page_path) + "\n"
        else: # Assume image
            full_text = extract_text_from_image(file_path)
        
        # Clean up temp files
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f))
            
    except Exception as e:
        # Clean up on error too
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f))
        print(f"Error processing file: {e}")
        return jsonify({'error': f'Error processing file. Is Poppler installed and path correct? Error: {e}'}), 500

    extracted_data = extract_key_values(full_text)
    return jsonify(extracted_data)


def preprocess_input(data):
    """
    Converts raw form data into the categorical format the model expects.
    """
    # 1. Convert Cholesterol (mg/dL) to category
    # Ranges: 1: <200 (Normal), 2: 200-239 (Above Normal), 3: >=240 (Well Above Normal)
    chol = int(data.get('cholesterol', 0))
    if chol < 200:
        data['Cholesterol'] = 1
    elif 200 <= chol < 240:
        data['Cholesterol'] = 2
    else:
        data['Cholesterol'] = 3
        
    # 2. Convert Glucose (mg/dL) to category
    # Ranges (fasting): 1: <100 (Normal), 2: 100-125 (Above Normal), 3: >=126 (Well Above Normal)
    gluc = int(data.get('gluc', 0))
    if gluc < 100:
        data['Gluc'] = 1
    elif 100 <= gluc < 126:
        data['Gluc'] = 2
    else:
        data['Gluc'] = 3

    # 3. Map string/form values to model's expected numbers
    # We assume 1=Male, 2=Female based on common datasets (your training data shows 1 and 2)
    data['Gender'] = 2 if data.get('gender') == 'female' else 1
    
    # We assume 0=No, 1=Yes for these, as is standard
    data['Smoke'] = 1 if data.get('smoke') == 'yes' else 0
    data['Alco'] = 1 if data.get('alco') == 'yes' else 0
    data['Active'] = 1 if data.get('active') == 'yes' else 0

    # 4. Prepare final DataFrame in the correct order
    # Note: 'Age ' key has a space, matching your training data
    input_data = {
        'Age ': [int(data.get('age', 0))],
        'Gender': [data['Gender']],
        'Height': [int(data.get('height', 0))],
        'Weight': [float(data.get('weight', 0))],
        'ap_hi': [int(data.get('ap_hi', 0))],
        'ap_lo': [int(data.get('ap_lo', 0))],
        'Cholesterol': [data['Cholesterol']],
        'Gluc': [data['Gluc']],
        'Smoke': [data['Smoke']],
        'Alco': [data['Alco']],
        'Active': [data['Active']]
    }
    
    # Create DataFrame with columns in the exact order the model expects
    df = pd.DataFrame(input_data, columns=EXPECTED_FEATURES)
    return df


@app.route('/predict', methods=['POST'])
def predict():
    """
    Receives form data, preprocesses it, and returns a model prediction.
    """
    if not model:
        return jsonify({'error': 'Model is not loaded.'}), 500
        
    try:
        data = request.get_json()
        
        # Preprocess the data (convert numeric chol/gluc to categories, etc.)
        processed_df = preprocess_input(data)

        # Make prediction
        prediction = model.predict(processed_df)
        probability = model.predict_proba(processed_df)

        # Format response
        risk_probability = probability[0][1] # Probability of class 1 (disease)
        
        # --- THIS IS THE FIX ---
        # Convert the final numpy.float32 to a standard Python float
        result = {
            'prediction': int(prediction[0]), # 0 or 1
            'probability': float(round(risk_probability * 100, 2)) 
        }
        return jsonify(result)
        
    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/feedback', methods=['POST'])
def handle_feedback():
    """Saves user feedback to a text file."""
    try:
        data = request.get_json()
        name = data.get('name', 'Anonymous')
        review = data.get('review', '')

        with open('feedback.txt', 'a') as f:
            f.write(f"Name: {name}\nReview: {review}\n{'-'*20}\n")
            
        return jsonify({'success': 'Feedback received!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- Frontend Page Routes ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/analyser')
def analyser():
    return render_template('analyser.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# --- Run the App ---
if __name__ == '__main__':
    # Creates 'temp_files' directory if it doesn't exist
    os.makedirs('temp_files', exist_ok=True) 
    app.run(debug=True)