# Lexicon: AI-Powered Text Analyzer

Python + Flask backend, SQLite database, responsive HTML/CSS/JS frontend.
Analysis: word frequency, keyword extraction, text statistics, sentiment.

## Run (Windows)
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python backend\app.py
Open http://127.0.0.1:5000

## Run (macOS/Linux)
    python3 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    python backend/app.py

## Structure
    backend/    app.py (API), analyzer.py (NLP), db.py (SQLite)
    frontend/   index.html, style.css, app.js
    database.db created automatically on first run
    requirements.txt
