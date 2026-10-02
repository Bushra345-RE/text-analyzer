from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

import db
from analyzer import analyze

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
app = Flask(__name__, static_folder=str(FRONTEND), static_url_path="")
CORS(app)
db.init()


@app.get("/")
def index():
    return send_from_directory(FRONTEND, "index.html")


@app.post("/api/analyze")
def api_analyze():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if len(text) < 3:
        return jsonify(error="Paste at least a few words to analyze."), 400
    if len(text) > 50000:
        return jsonify(error="Text is too long. The limit is 50,000 characters."), 400
    result = analyze(text)
    saved_id = None
    if data.get("save", True):
        title = (data.get("title") or text[:40]).strip()
        saved_id = db.save(title, text, result)
    return jsonify(id=saved_id, result=result)


@app.get("/api/history")
def api_history():
    return jsonify(db.history())


@app.get("/api/history/<int:i>")
def api_get(i):
    row = db.get(i)
    return (jsonify(row), 200) if row else (jsonify(error="Not found"), 404)


@app.delete("/api/history/<int:i>")
def api_delete(i):
    db.delete(i)
    return "", 204


if __name__ == "__main__":
    app.run(debug=True, port=5000)
