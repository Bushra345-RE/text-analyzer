"""Pure-Python NLP: statistics, word frequency, keyword extraction, sentiment."""
import math
import re
from collections import Counter

STOPWORDS = set("""a about above after again all am an and any are as at be because been before being below between
both but by can could did do does doing down during each few for from further had has have having he her here hers
him his how i if in into is it its itself just me more most my no nor not now of off on once only or other our out
over own same she should so some such than that the their them then there these they this those through to too
under until up very was we were what when where which while who whom why will with would you your yours also
like get got one us""".split())

POSITIVE = set("""good great excellent amazing awesome love loved lovely happy joy wonderful fantastic best better
beautiful brilliant nice perfect enjoy enjoyed enjoyable positive success successful smart helpful easy fast
useful powerful elegant clean impressive delightful pleasant glad exciting excited win strong improve improved
fun favorite recommend reliable""".split())

NEGATIVE = set("""bad terrible awful horrible hate hated sad angry worst worse poor ugly boring slow broken fail
failed failure difficult hard painful negative problem problems bug bugs annoying useless weak disappointing
disappointed confusing error errors wrong lose lost fear scary dull messy buggy""".split())

NEGATIONS = {"not", "no", "never", "hardly", "without", "isn't", "wasn't", "don't", "doesn't", "didn't", "can't", "won't"}
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'’-]*")


def _sentiment(tokens):
    pos = neg = 0
    for i, tok in enumerate(tokens):
        flipped = any(w in NEGATIONS for w in tokens[max(0, i - 2):i])
        if tok in POSITIVE:
            neg, pos = (neg + 1, pos) if flipped else (neg, pos + 1)
        elif tok in NEGATIVE:
            pos, neg = (pos + 1, neg) if flipped else (pos, neg + 1)
    total = pos + neg
    score = 0.0 if total == 0 else (pos - neg) / math.sqrt(total * total + 4)
    label = "Positive" if score > 0.15 else "Negative" if score < -0.15 else "Neutral"
    return {"score": round(score, 3), "label": label, "positive": pos, "negative": neg}


def analyze(text: str) -> dict:
    text = text.strip()
    tokens = [t.lower().strip("'’-") for t in WORD_RE.findall(text)]
    tokens = [t for t in tokens if t]
    words = len(tokens)
    sentences = [s for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    content = [t for t in tokens if t not in STOPWORDS and len(t) > 2]

    freq = Counter(content)
    top_words = [{"word": w, "count": c} for w, c in freq.most_common(10)]

    scores = {w: c * (1 + min(len(w), 12) / 12) for w, c in freq.items()}
    bigrams = Counter(
        f"{a} {b}" for a, b in zip(tokens, tokens[1:])
        if a not in STOPWORDS and b not in STOPWORDS and len(a) > 2 and len(b) > 2
    )
    for bg, c in bigrams.items():
        if c >= 2:
            scores[bg] = c * 3
    top = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:12]
    peak = top[0][1] if top else 1
    keywords = [{"term": k, "weight": round(v / peak, 2)} for k, v in top]

    return {
        "stats": {
            "characters": len(text), "words": words, "sentences": len(sentences),
            "paragraphs": len(paragraphs),
            "avg_word_length": round(sum(map(len, tokens)) / words, 1) if words else 0,
            "avg_sentence_length": round(words / len(sentences), 1) if sentences else 0,
            "unique_words": len(set(tokens)),
            "lexical_diversity": round(len(set(tokens)) / words, 2) if words else 0,
            "reading_time_min": round(words / 200, 1),
        },
        "top_words": top_words, "keywords": keywords, "sentiment": _sentiment(tokens),
    }
