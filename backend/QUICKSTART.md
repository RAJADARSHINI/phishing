# Quick Start Guide

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

## Step-by-Step Setup

### 1. Navigate to backend directory
```bash
cd backend
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Prepare your data files

Place your CSV files in the `data/` directory:
- `data/enron_spam.csv` - Email spam dataset
- `data/phishing_sites.csv` - URL phishing dataset

**Or use the setup helper:**
```bash
python setup_data.py
```

This will search for CSV files and organize them.

### 4. Train the models
```bash
python train_models.py
```

This will:
- Load and preprocess your data
- Train machine learning models
- Save models to `models/` directory
- Display training accuracy and metrics

### 5. Start the API server
```bash
python app.py
```

The API will be available at `http://localhost:8000`

### 6. Test the API

**Option A: Run the test script**
```bash
python test_api.py
```

**Option B: Run example usage**
```bash
python example_usage.py
```

**Option C: Test with curl**
```bash
curl -X POST "http://localhost:8000/predict-email" \
  -H "Content-Type: application/json" \
  -d '{"text": "You have won $1000000!"}'
```

## Expected CSV Format

Your CSV files should have:
- A column named `text` (or similar) containing email/URL text
- A column with labels: `labels`, `label`, `spam`, or `phishing`
  - Values: `0` = safe/not spam, `1` = phishing/spam

Example:
```csv
text,labels
"You have won $1000000!",1
"Meeting scheduled for tomorrow",0
```

## Troubleshooting

### Models not found error
- Make sure you've run `python train_models.py` first
- Check that `models/` directory contains `.pkl` files

### CSV file not found
- Place CSV files in `data/` directory
- Or run `python setup_data.py` to organize files
- Check file names match exactly: `enron_spam.csv` and `phishing_sites.csv`

### Port already in use
- Change the port in `app.py`: `uvicorn.run(app, host="0.0.0.0", port=8001)`
- Or stop the process using port 8000

### Import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Use a virtual environment to avoid conflicts

## Next Steps

- Integrate with your frontend (API endpoints are ready)
- Customize models (edit `train_models.py`)
- Add more features (extend preprocessing in `app.py`)
- Deploy to production (consider adding authentication, rate limiting)
