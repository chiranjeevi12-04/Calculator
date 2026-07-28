# Streamlit + FastAPI Calculator

A realistic calculator UI in Streamlit with arithmetic handled by a FastAPI backend.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

Open two PowerShell terminals from this folder.

Terminal 1:

```powershell
uvicorn api:app --reload
```

Terminal 2:

```powershell
streamlit run app.py
```

FastAPI runs at `http://127.0.0.1:8000`.
Streamlit usually opens at `http://localhost:8501`.
