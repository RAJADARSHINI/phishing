# 🚀 Phishing Detection - Quick Start Guide

## ⚡ Quick Start (Recommended)

### Option 1: Using Startup Scripts (Easiest)

**Windows (PowerShell - Recommended):**
```powershell
cd backend
.\start_backend.ps1
```

**Windows (Command Prompt):**
```cmd
cd backend
start_backend.bat
```

These scripts automatically:
- Kill any existing process on port 8000
- Start the backend cleanly
- Handle port conflicts automatically

### Option 2: Manual Start

1. **Kill existing backend process (if any):**
   ```powershell
   # PowerShell
   Get-NetTCPConnection -LocalPort 8000 -State Listen | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
   ```

2. **Start backend:**
   ```bash
   cd backend
   python app.py
   ```

3. **Start frontend (in new terminal):**
   ```bash
   npm run dev
   ```

## 🔧 Troubleshooting

### Port 8000 Already in Use

**Symptom:** `[Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)`

**Solution 1 - Use startup script:**
```cmd
cd backend
start_backend.bat
```

**Solution 2 - Manual kill:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /F /PID <PID>

# Then start backend
python backend\app.py
```

**Solution 3 - Automatic fallback:**
The backend now automatically tries ports 8000-8009. If 8000 is occupied, it will use the next available port and notify you.

### Frontend Can't Connect to Backend

**Check:**
1. Backend is running (you should see "Starting server on port 8000")
2. Frontend proxy is configured correctly in `vite.config.ts`
3. No firewall blocking localhost connections

**Fix:**
- Restart both backend and frontend
- Check browser console for CORS errors
- Verify backend URL in frontend requests

### Models Not Loading

**Symptom:** Backend starts but analysis returns dummy results

**Solution:**
```bash
cd backend
python train_models.py
```

This will train and save the models to the `models/` directory.

## 📡 API Endpoints

Once running, the backend provides:

- **GET** `/` - API information
- **POST** `/predict-email` - Predict if email is spam
- **POST** `/predict-url` - Predict if URL is phishing
- **POST** `/analyze_email` - Comprehensive analysis (used by frontend)
- **WS** `/ws/analyze` - WebSocket for real-time progress
- **GET** `/api/stats` - Dashboard statistics

## 🧪 Testing the Backend

```bash
cd backend
python test_api.py
```

## 🎯 Expected Flow

1. **Start Backend** → Server runs on port 8000 (or next available)
2. **Start Frontend** → Vite dev server runs on port 5173
3. **User inputs data** → Text, URL, or image
4. **Frontend sends request** → `/analyze_email` endpoint
5. **Backend analyzes** → Using NLP and URL models
6. **Backend returns JSON:**
   ```json
   {
     "nlp_score": 0.85,
     "url_score": 0.72,
     "vision_score": 0.0,
     "risk_score": 0.81,
     "explainability": {
       "factors": ["Email text shows high spam indicators"],
       "warnings": ["Suspicious URL detected: http://..."]
     }
   }
   ```
7. **Frontend displays results** → Risk score and explanation

## 🔍 Current Status

- ✅ Backend: FastAPI with auto-port detection
- ✅ Frontend: React + Vite with proxy configuration
- ✅ CORS: Configured for localhost
- ✅ Models: NLP and URL models loaded
- ✅ Startup Scripts: Automated process management

## 📝 Notes

- Backend automatically finds available port (8000-8009)
- Frontend proxy is configured for port 8000 (update if backend uses different port)
- Startup scripts handle port conflicts automatically
- No frontend UI changes required
