# Phishing Detection Backend

Python backend for phishing and spam detection using machine learning models.

## Features

- **Email Spam Detection**: Analyzes email text to detect spam
- **URL Phishing Detection**: Analyzes URLs to detect phishing attempts
- **REST API**: FastAPI-based endpoints for predictions
- **WebSocket Support**: Real-time progress updates for analysis
- **Model Training**: Scripts to train and save ML models

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Data

Place your CSV files in the `data/` directory:
- `data/enron_spam.csv` - Email spam dataset (columns: `text`, `labels` or `label` or `spam`)
- `data/phishing_sites.csv` - URL phishing dataset (columns: `text`, `labels` or `label` or `phishing`)

**Note**: The CSV files should have:
- A column with email/URL text (named `text`)
- A column with labels (0 = safe/not spam, 1 = phishing/spam)

**Quick Setup**: Run the setup helper script to organize your CSV files:
```bash
python setup_data.py
```

This script will:
- Create the `data/` directory if it doesn't exist
- Search for CSV files in common locations
- Copy them to the `data/` directory
- Validate the file structure

### 3. Train Models

Train the machine learning models:

```bash
python train_models.py
```

This will:
- Load and preprocess the data
- Train Logistic Regression and Random Forest models
- Save models to `models/` directory:
  - `models/email_model.pkl`
  - `models/email_vectorizer.pkl`
  - `models/url_model.pkl`
  - `models/url_vectorizer.pkl`

### 4. Run the API Server

Start the FastAPI server:

```bash
python app.py
```

Or using uvicorn directly:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Predict Email Spam

**POST** `/predict-email`

Request body:
```json
{
  "text": "Click here to claim your prize!"
}
```

Response:
```json
{
  "prediction": 1,
  "probability": 0.85,
  "confidence": 0.70
}
```

### 2. Predict URL Phishing

**POST** `/predict-url`

Request body:
```json
{
  "url": "http://paypal-security-verify.com"
}
```

Response:
```json
{
  "prediction": 1,
  "probability": 0.92,
  "confidence": 0.84
}
```

### 3. Comprehensive Analysis (Frontend Integration)

**POST** `/analyze_email`

Request body:
```json
{
  "text": "Click here to verify your account: http://suspicious-site.com",
  "urls": ["http://suspicious-site.com"],
  "images_b64": []
}
```

Response:
```json
{
  "risk_score": 0.75,
  "nlp_score": 0.80,
  "url_score": 0.70,
  "vision_score": 0.0,
  "explainability": {
    "factors": [
      "Email text shows high spam indicators",
      "Suspicious URLs detected in the message"
    ],
    "warnings": [
      "Suspicious URL detected: http://suspicious-site.com"
    ]
  }
}
```

### 4. WebSocket for Progress Updates

**WS** `/ws/analyze`

Connects via WebSocket and sends analysis request:
```json
{
  "text": "Email text here",
  "urls": ["url1", "url2"],
  "images_b64": []
}
```

Receives progress updates and final result.

## Testing

Run the test script:

```bash
python test_api.py
```

Or test manually using curl:

```bash
# Test email prediction
curl -X POST "http://localhost:8000/predict-email" \
  -H "Content-Type: application/json" \
  -d '{"text": "You have won $1000000! Click now!"}'

# Test URL prediction
curl -X POST "http://localhost:8000/predict-url" \
  -H "Content-Type: application/json" \
  -d '{"url": "http://paypal-security-verify.com"}'
```

### Python Example

```python
import requests

# Predict email spam
response = requests.post(
    "http://localhost:8000/predict-email",
    json={"text": "You have won $1000000! Click now!"}
)
result = response.json()
print(f"Prediction: {'SPAM' if result['prediction'] == 1 else 'NOT SPAM'}")
print(f"Probability: {result['probability']:.2%}")

# Predict URL phishing
response = requests.post(
    "http://localhost:8000/predict-url",
    json={"url": "http://paypal-security-verify.com"}
)
result = response.json()
print(f"Prediction: {'PHISHING' if result['prediction'] == 1 else 'SAFE'}")
print(f"Probability: {result['probability']:.2%}")
```

## Quick Start (All-in-One)

For a quick setup, use the provided scripts:

**Linux/Mac:**
```bash
chmod +x quick_start.sh
./quick_start.sh
```

**Windows:**
```cmd
quick_start.bat
```

These scripts will:
1. Create a virtual environment
2. Install dependencies
3. Set up data directory
4. Train models
5. Start the API server

## Project Structure

```
backend/
├── app.py                 # FastAPI application
├── train_models.py        # Model training script
├── setup_data.py          # Data setup helper
├── test_api.py            # Test script
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── quick_start.sh         # Quick start script (Linux/Mac)
├── quick_start.bat        # Quick start script (Windows)
├── data/                  # CSV data files (created by setup)
│   ├── enron_spam.csv
│   └── phishing_sites.csv
└── models/                # Trained models (created after training)
    ├── email_model.pkl
    ├── email_vectorizer.pkl
    ├── url_model.pkl
    └── url_vectorizer.pkl
```

## Integration with Frontend

The backend is designed to work with the existing React frontend:

1. The frontend calls `POST /analyze_email` with `{ text, urls, images_b64 }`
2. The backend returns `PhishingAnalysisResponse` with risk scores
3. WebSocket endpoint `/ws/analyze` provides real-time progress updates

Make sure CORS is configured correctly (currently set to allow all origins for development).

## Model Details

- **Email Model**: Uses TF-IDF vectorization with Logistic Regression
- **URL Model**: Uses character-based TF-IDF n-grams with Logistic Regression
- Both models are trained on labeled datasets and saved as pickle files

## Notes

- Models must be trained before running the API server
- The API loads models on startup
- For production, consider:
  - Adding authentication
  - Restricting CORS origins
  - Using environment variables for configuration
  - Adding rate limiting
  - Implementing proper logging
