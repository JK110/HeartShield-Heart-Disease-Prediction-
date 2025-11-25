# HeartShield

Markdown

# HeartShield: AI-Powered Heart Disease Risk Analyser



**HeartShield** is a comprehensive web application designed to provide early warnings for cardiovascular diseases using Machine Learning. It allows users to predict their heart disease risk by manually entering health metrics or by **uploading medical reports (PDF/Images)**, from which data is automatically extracted using OCR.

The system features a robust clinical safety net, user profiles with history tracking, and integrated geolocation services to suggest nearby cardiologists in high-risk scenarios.

---

## 🚀 Key Features

* **🤖 AI Prediction Engine:** Uses an **XGBoost** model trained on thousands of patient records to predict risk probability.
* **📄 Smart OCR Extraction:** Upload medical reports (PDF/JPG/PNG). The system extracts key vitals (BP, Cholesterol, Glucose) and auto-fills the analysis form.
* **🛡️ Clinical Safety Net:** Overrides AI predictions for critical values (e.g., Hypertensive Crisis, Severe Diabetes) to ensure user safety.
* **👤 User Profiles & History:** * Secure Registration & Login.
    * Edit Profile details (Age, Weight, Height) for "Smart Filling" logic.
    * Dashboard to view the **last 5 prediction results**.
   
* **🏥 Emergency Response:** * **Geolocation Integration:** Automatically finds nearby hospitals/cardiologists on Google Maps for high-risk users.
    * **Online Consultancy:** Direct links to Practo, MediBuddy, and Lybrate.
* **📸 Advanced UI:** * Document Preview with Zoom In/Out.
    * **Webcam Support** to capture reports directly from the browser.
    * Responsive Design for Mobile and Desktop.

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask, SQLAlchemy
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
* **Database:** MySQL
* **Machine Learning:** Scikit-learn, XGBoost, Pandas, NumPy
* **Image Processing / OCR:** OpenCV, Pytesseract, PDF2Image, Poppler


---

## 📂 Project Structure

```text
HeartShield_Project/
│
├── app.py                       # Main Flask Application
├── best_xgboost_model.pkl       # Trained ML Model
├── feedback.txt                 # User Feedback Log
├── requirements.txt             # Python Dependencies
│
├── templates/                   # HTML Pages
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── analyser.html
│   ├── about.html
│   └── contact.html
│
└── static/                      # Static Assets
    ├── css/
    │   └── style.css
    ├── js/
    │   └── script.js
    ├── images/                  # Site Backgrounds & Assets
    │   ├── heartshield-logo.jpg
    │   ├── hero-backgroundfinal.jpg
    │   └── ... (other assets)
    │
    └── profile_pics/            # User Uploads
        └── default.jpg          # Required default image
⚙️ Installation & Setup
1. Prerequisites
Ensure you have the following installed:

Python 3.8+

MySQL Server

Tesseract OCR (Required for Image text extraction)

Poppler (Required for PDF to Image conversion)

2. Clone the Repository
Bash

git clone [https://github.com/your-username/HeartShield.git](https://github.com/your-username/HeartShield.git)
cd HeartShield
3. Install Dependencies
Bash

pip install -r requirements.txt
If requirements.txt is missing, install manually:

Bash

pip install flask flask-sqlalchemy flask-login pymysql pandas numpy scikit-learn xgboost opencv-python pytesseract pdf2image email_validator
4. Database Setup
Open your MySQL Workbench/CLI.

Create the database:

SQL

CREATE DATABASE heartshield_db;
Open app.py and update the database connection string with your password:

Python

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:YOUR_PASSWORD@localhost/heartshield_db'
5. Configure OCR Paths (Windows)
If Tesseract or Poppler are not in your system PATH, update app.py:

Python

# Inside app.py

# Tesseract Path
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Poppler Path (Inside handle_extraction function)
poppler_path = r"C:\Program Files\poppler-xx\bin"
6. Required Files Check
Ensure these files exist before running:

best_xgboost_model.pkl in the root folder.

static/profile_pics/default.jpg (Place any placeholder image here).

🏃‍♂️ Usage
Run the application:

Bash

python app.py
Open your browser and go to:

[http://127.0.0.1:5000/](http://127.0.0.1:5000/)
Sign Up to create an account (Fill in your Age/Weight/Height for better automation).

Go to Analyser. Upload a report or manually enter values.

Click Analyse Risk to get your prediction.
