# Deployment Guide 🚀

This project is now ready for production deployment. You have several options:

## 1. Using Docker Compose (Recommended for local/private server)
The easiest way to run both the backend and frontend together:

```bash
docker-compose up --build
```
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:8501

## 2. Deploying to Render / Render.com
### Backend (FastAPI)
- **Service Type**: Web Service
- **Runtime**: Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

### Frontend (Streamlit)
- **Service Type**: Web Service
- **Runtime**: Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
- **Environment Variable**: Set `API_URL` to your Backend URL + `/extract-pdf` (e.g., `https://your-backend.onrender.com/extract-pdf`)

## 3. Manual Deployment (Linux Server)
If you are deploying manually on a VPS:

**Run Backend:**
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Run Frontend:**
```bash
streamlit run app.py --server.port 8501
```

## Production Checklist
- [x] CORS enabled in `main.py`
- [x] Environment variable support for `API_URL` in `app.py`
- [x] Production-grade server (`gunicorn`) added to `requirements.txt`
- [x] Dockerization complete
