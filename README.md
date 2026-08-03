# Cited Sports Encyclopedia

A portfolio-grade RAG application that answers questions based *strictly* on two small datasets (world cricketers and Indian Olympic athletes), citing every fact and gracefully handling complex name collisions. 

## Features
- **Entity-Grounded Adaptive RAG**: A composite architecture preventing hallucinations and misattributions.
- **Strict Citation Verification**: Uses Self-RAG verification to critique LLM drafts and fall back to deterministic templates if facts aren't grounded.
- **Pre-Generation Refusal**: Corrective RAG gates queries for absent entities or attributes, stopping hallucinations before they occur.
- **Robust Collision Handling**: Deterministically handles overlaps across sports, brothers (Waugh), or identical surnames (Khan).

## Setup Instructions

### 1. Requirements
- Python 3.11+
- Node.js 18+

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # (or venv\Scripts\activate on Windows)
pip install -r requirements.txt
```

Set your API key in `backend/.env`:
```
GROQ_API_KEY=your_key_here
```

### 3. Data Processing Pipeline
Assuming your raw data files are in `backend/data/raw/`:
```bash
# Parse Excel files into JSON and run validation checks
python -m app.ingestion.load_datasets --validate

# Build embeddings, FAISS vector index, and collision index
python -m app.ingestion.build_index --verify-collisions
```

### 4. Running the App
Start the backend API (FastAPI):
```bash
cd backend
uvicorn app.main:app --reload
```

Start the frontend (Vite React app):
```bash
cd frontend
npm install
npm run dev
```

### 5. Running the Acceptance Suite
```bash
cd backend
# Make sure to set PYTHONPATH
$env:PYTHONPATH="."  # (Windows PowerShell)
export PYTHONPATH="." # (Linux/Mac)
pytest tests/test_acceptance_suite.py -v
```
