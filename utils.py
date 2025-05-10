# utils.py
import json
import os

STATS_FILE = 'data/stats.json'

def load_stats():
    if not os.path.exists(STATS_FILE):
        return { "high_wpm": 0,
            "high_accuracy": 0,
            "high_score": 0,
            "total_words": 0}
    with open(STATS_FILE, 'r') as file:
        return json.load(file)

def save_stats(stats):
    with open(STATS_FILE, 'w') as file:
        json.dump(stats, file, indent=4)
