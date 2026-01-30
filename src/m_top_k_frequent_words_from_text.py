# Auto-generated module
def m_top_k_frequent_words_from_text(text: str, k: int = 10):
    """Return list of (word, count) sorted by descending frequency then name."""
    words = [w.lower() for w in text.split() if w.isalpha()]
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    items = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
    return items[:k]
