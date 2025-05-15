# utils/io.py

import json

def load_transitions(file_path="transitions.json"):
    """
    Load a list of 5-word transition phrases from a JSON file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
